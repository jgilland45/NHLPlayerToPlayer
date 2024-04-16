<template>
  <div
    v-if="filteredData.length && filter.length > 2"
    class="search-block-container"
  >
    <PlayerBlock
      v-for="datum in filteredData"
      :key="datum.URL"
      :player="datum"
      class="player-block"
      @click="onSelect(datum.URL)"
    />
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'
import PlayerBlock from '@/components/PlayerBlock.vue'
import Fuse from 'fuse.js'

const props = defineProps({
    data: Array,
    filterKey: String
})

const emit = defineEmits(['choose'])

// https://stackoverflow.com/questions/990904/remove-accents-diacritics-in-a-string-in-javascript
const filter = computed(() => props.filterKey.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase())

const onSelect = (player) => {
    console.log('select: ', player)
    emit('choose', player)
}

const filteredData = computed(() => {
    let unfilteredData = [...props.data]
    if (filter.value) {
        unfilteredData = unfilteredData.map((d) => ({
            ...d,
            searchName: d.NAME.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()
        }))
    }
    const fuseOptions = {
        // isCaseSensitive: false,
        // includeScore: false,
        // shouldSort: true,
        // includeMatches: false,
        // findAllMatches: false,
        // minMatchCharLength: 1,
        // location: 0,
        threshold: 0.3,
        // distance: 100,
        // useExtendedSearch: false,
        // ignoreLocation: false,
        // ignoreFieldNorm: false,
        // fieldNormWeight: 1,
        keys: ['searchName']
    }
    const fuse = new Fuse(unfilteredData, fuseOptions)
    console.log(filter.value)
    console.log(fuse.search(filter.value))
    return filter.value ? fuse.search(filter.value).map(d => d.item) : []
})
</script>

<style lang="postcss" scoped>
.search-block-container {
  @apply absolute top-60 flex flex-col border-2 border-black h-fit max-h-[608px] overflow-y-auto z-10;
  .player-block {
    @apply flex-auto pl-1 text-xl border-b border-black w-full min-w-[350px] max-w-xl bg-white cursor-pointer select-none;
    &:last-child {
      @apply border-none;
    }
  }
}
</style>
