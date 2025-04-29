<template>
  <div class="players-list">
    <InputSearch v-model="searchTerm" />

    <div ref="scrollParentRef" class="scroller">
      <div :style="{ height: totalHeight + 'px', position: 'relative' }">
        <div
          v-for="virtualRow in virtualRows"
          :style="{
            position: 'absolute',
            top: virtualRow.start + 'px',
            width: '100%',
          }"
        >
          <PlayerCard
            :player-name="filteredResults[virtualRow.index].item.name"
            :player-image-u-r-l="getImageUrl(filteredResults[virtualRow.index].item)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, watchEffect, onMounted } from 'vue';
import InputSearch from './InputSearch.vue';
import PlayerCard from './PlayerCard.vue';
import { useFuse } from '@vueuse/integrations/useFuse';
import { useVirtualizer, Virtualizer } from '@tanstack/vue-virtual';

type Player = {
  playerid: number;
  name: string;
  image_url?: string;
}

const searchTerm = ref<string>('');
const players = ref<Player[]>([])
const loadedImageCache = new Map<number, string>() // playerid -> url

const options = computed(() => ({
  fuseOptions: {
    threshold: 0.3,
    keys: ['name'],
  },
}));

const { results: fuseResults, fuse } = useFuse(searchTerm, players, options);
// Filtered results to display
const filteredResults = computed(() => fuseResults.value);

const scrollParentRef = ref<HTMLElement | null>(null);

const rowVirtualizer = ref<ReturnType<typeof useVirtualizer> | null>(null)

const virtualRows = computed(() => rowVirtualizer.value?.getVirtualItems() ?? []);
const totalHeight = computed(() => rowVirtualizer.value?.getTotalSize() ?? 0);

const onPlayerChoiceClick = (idx: number) => {
  console.log(players.value[idx]);
};

async function fetchPlayers() {
  try {
    const response = await fetch('http://127.0.0.1:8000/players');
    const data: { players: { playerid: number; name: string }[] } = await response.json();

    players.value = data.players.map(player => ({
      ...player,
      image_url: undefined,
    }));

    // set fuse collection
    fuse.value.setCollection(players.value);
    console.log(players.value);
    // Now that players are loaded, create virtualizer
    rowVirtualizer.value = useVirtualizer<HTMLElement, Element>({
      count: players.value.length,
      getScrollElement: () => scrollParentRef.value,
      estimateSize: () => 120,
  })
  } catch (error) {
    console.error('Error fetching players:', error);
  }
}

// Dynamically fetch image when needed
async function fetchImageIfNeeded(player: Player) {
  if (player.playerid && !loadedImageCache.has(player.playerid)) {
    try {
      const imageRes = await fetch(`http://127.0.0.1:8000/player/${player.playerid}/image`);
      const imageData = await imageRes.json();
      loadedImageCache.set(player.playerid, imageData.image_url);
    } catch (error) {
      console.error(`Failed to load image for player ${player.playerid}`, error);
      loadedImageCache.set(player.playerid, 'https://assets.nhle.com/mugs/nhl/default-skater.png');
    }
  }
}

// Helper to get current image url (either cached or placeholder)
function getImageUrl(player: Player) {
  // Start fetching in background if not already
  fetchImageIfNeeded(player);
  
  // Return what we have
  return loadedImageCache.get(player.playerid) ?? 'https://assets.nhle.com/mugs/nhl/default-skater.png';
}

watchEffect(() => {
  console.log('filteredResults:', filteredResults.value)
  console.log('count (should match filteredResults.length):', filteredResults.value.length)
})

watchEffect(() => {
  console.log('virtualRows:', virtualRows.value)
})

watchEffect(() => {
  console.log('totalHeight:', totalHeight.value)
})

onMounted(fetchPlayers);
</script>

<style scoped lang="postcss">
.players-list {
  height: 90vh;
  display: flex;
  flex-direction: column;

  .scroller {
    height: 90vh;
    overflow: auto;
    position: relative;
    flex-grow: 1;
  }
}
</style>