<template>
  <div
    ref="containerRef"
    class="search-with-results-container"
  >
    <InputSearch
      class="search"
      v-model="inputText"
    />

    <div
      v-if="players.length"
      class="results-dropdown"
    >
      <PlayerCard
        v-for="player in players"
        :key="player.id"
        :player-name="player.full_name"
        :player-image-u-r-l="player.photo_url"
        @click="clickPlayerCard(player)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import InputSearch from '@/components/InputSearch.vue';
import PlayerCard from '@/components/PlayerCard.vue';
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { debounce } from 'lodash-es';

export type Player = {
  id: number;
  full_name: string;
  photo_url: string;
}

const API_URL = `${import.meta.env.DEV ? '/api' : 'http://127.0.0.1:8000'}/players/search/`;

const inputText = ref<string>("");
const players = ref<Player[]>([]);
const containerRef = ref<HTMLElement | null>(null);

const clickPlayerCard = (player: Player) => {
  emit("click", player);
  inputText.value = "";
  players.value = [];
};

const closeDropdown = () => {
  players.value = [];
};

const handleDocumentClick = (event: MouseEvent) => {
  if (!containerRef.value) return;
  const target = event.target as Node | null;
  if (target && !containerRef.value.contains(target)) {
    closeDropdown();
  }
};

const handleEscape = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    closeDropdown();
  }
};

const emit = defineEmits<{
  click: [player: Player],
}>();

watch(inputText, debounce(async (newVal: string) => {
  if (!newVal) {
    players.value = [];
    return;
  }
  const url = `${API_URL}${newVal}`;
  const rawPlayerData: { id: number; full_name: string }[] = await (await fetch(url)).json();
  const mappedPlayers = rawPlayerData.map((player: { id: number; full_name: string }) => {
    const image_url = `https://assets.nhle.com/mugs/nhl/latest/${player.id}.png`;
    return {
      id: player.id,
      full_name: player.full_name,
      photo_url: image_url,
    }
  });
  console.log(mappedPlayers);
  players.value = mappedPlayers;
}, 250));

onMounted(() => {
  document.addEventListener('mousedown', handleDocumentClick);
  document.addEventListener('keydown', handleEscape);
});

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleDocumentClick);
  document.removeEventListener('keydown', handleEscape);
});

</script>

<style lang="postcss" scoped>
.search-with-results-container {
  @apply relative w-full;
}

.search {
  @apply h-10 bg-white;
}

.results-dropdown {
  @apply absolute left-0 right-0 top-[44px] z-30 max-h-[320px] overflow-y-auto rounded border border-slate-700 bg-slate-900 p-1 shadow-lg;
}
</style>
