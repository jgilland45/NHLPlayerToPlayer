<template>
    <div class="search-container">
        <input
            aria-label="Search for a player..."
            type="text"
            class="search-input"
            placeholder="Search for a player..."
            v-model="text"
        >
        <div class="icon-container">
            <Icon icon="material-symbols:search" />
        </div>
    </div>
</template>

<script lang="js" setup>
import { ref, watch, defineEmits, defineProps } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps({
    searchText: String
})

const emit = defineEmits(['search'])

const text = ref(props.searchText)

watch(text, (value) => {
    emit('search', value)
})
</script>

<style lang="postcss" scoped>
.search-container {
    @apply w-full flex flex-row relative;
    .search-input {
        @apply w-full py-4 pr-3 pl-10 border border-black rounded-md;
        font-size: 16px;

        &::placeholder {
            @apply text-gray-500 font-normal text-base;
        }
    }
    .icon-container {
        @apply absolute left-3 top-0 h-full flex items-center text-gray-500;
    }
}
</style>
