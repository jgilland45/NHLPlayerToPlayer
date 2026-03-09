<template>
  <main class="home-view">
    <h1>Teammate Path Game</h1>
    <p class="subtitle">Start from one player and keep naming valid teammates until you reach the target.</p>

    <div class="controls">
      <button
        class="action-btn"
        :disabled="loading"
        @click="startGame"
      >
        {{ loading ? 'Starting...' : 'Start New Game' }}
      </button>

      <button
        v-if="sessionId && !completed && !gaveUp"
        class="action-btn danger"
        :disabled="loading"
        @click="giveUp"
      >
        Give Up
      </button>

      <button
        v-if="sessionId && (completed || gaveUp)"
        class="action-btn secondary"
        :disabled="loading"
        @click="showOptimalSolution"
      >
        Show Optimal Solution
      </button>
    </div>

    <p
      v-if="statusMessage"
      class="status"
    >
      {{ statusMessage }}
    </p>

    <p
      v-if="errorBanner"
      class="error-banner"
    >
      {{ errorBanner }}
    </p>

    <section
      v-if="startPlayer && endPlayer"
      class="targets"
    >
      <div class="target-card">
        <h2>Start Player</h2>
        <PlayerCard
          :player-name="startPlayer.full_name"
          :player-image-u-r-l="getPlayerImage(startPlayer.id)"
        />
      </div>

      <div class="target-card">
        <h2>Finish Player</h2>
        <PlayerCard
          :player-name="endPlayer.full_name"
          :player-image-u-r-l="getPlayerImage(endPlayer.id)"
        />
      </div>
    </section>

    <section
      v-if="sessionId && !completed && !gaveUp"
      class="guess-section"
    >
      <h2>Pick Your Next Teammate</h2>
      <SearchWithResults @click="submitGuess" />
    </section>

    <section
      v-if="currentPath.length"
      class="path-section"
    >
      <h2>Your Path</h2>

      <div
        v-if="noLinkPopups.length"
        class="no-link-popups"
      >
        <NoLinkToPlayer
          v-for="popup in noLinkPopups"
          :key="popup.id"
          :player-name="popup.playerName"
        />
      </div>

      <div
        ref="yourPathScrollRef"
        class="path-visual-scroll"
      >
        <div
          v-for="(player, index) in currentPath"
          :key="`path-player-${player.id}-${index}`"
          class="path-node"
        >
          <div class="path-player-card">
            <PlayerCard
              :player-name="player.full_name"
              :player-image-u-r-l="getPlayerImage(player.id)"
            />
          </div>

          <div
            v-if="index < pathConnections.length"
            class="path-connection"
          >
            <TeamConnectionBundle :team-connections="pathConnections[index]" />
            <span class="path-arrow">↓</span>
          </div>
        </div>
      </div>
    </section>

    <section
      v-if="optimalPath.length"
      class="optimal-section"
    >
      <h2>Optimal Solution</h2>
      <p>Shortest path length: {{ shortestPathLength }}</p>

      <div class="path-visual-scroll">
        <div
          v-for="(player, index) in optimalPath"
          :key="`optimal-player-${player.id}-${index}`"
          class="path-node"
        >
          <div class="path-player-card">
            <PlayerCard
              :player-name="player.full_name"
              :player-image-u-r-l="getPlayerImage(player.id)"
            />
          </div>

          <div
            v-if="index < optimalConnections.length"
            class="path-connection"
          >
            <TeamConnectionBundle :team-connections="optimalConnections[index]" />
            <span class="path-arrow">↓</span>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { nextTick, ref } from 'vue';

import NoLinkToPlayer from '@/components/NoLinkToPlayer.vue';
import PlayerCard from '@/components/PlayerCard.vue';
import SearchWithResults, { type Player as SearchPlayer } from '@/components/SearchWithResults.vue';
import TeamConnectionBundle, { type TeamConnection } from '@/components/TeamConnectionBundle.vue';

type ApiPlayer = {
  id: number;
  full_name: string;
};

type PopupEntry = {
  id: number;
  playerName: string;
};

const API_BASE_URL = import.meta.env.DEV ? '/api' : 'http://127.0.0.1:8000';
const REQUEST_TIMEOUT_MS = 15000;

const loading = ref(false);
const sessionId = ref<string | null>(null);
const startPlayer = ref<ApiPlayer | null>(null);
const endPlayer = ref<ApiPlayer | null>(null);
const currentPath = ref<ApiPlayer[]>([]);
const optimalPath = ref<ApiPlayer[]>([]);
const optimalConnections = ref<TeamConnection[][]>([]);
const shortestPathLength = ref(0);
const completed = ref(false);
const gaveUp = ref(false);
const statusMessage = ref('Click "Start New Game" to begin.');
const errorBanner = ref<string | null>(null);
const pathConnections = ref<TeamConnection[][]>([]);
const noLinkPopups = ref<PopupEntry[]>([]);
const popupCounter = ref(0);
const yourPathScrollRef = ref<HTMLElement | null>(null);

const getPlayerImage = (playerId: number) => `https://assets.nhle.com/mugs/nhl/latest/${playerId}.png`;
const getTeamLogoFromLabel = (teamSeasonLabel: string) => {
  const tricode = teamSeasonLabel.split(' ')[0]?.toUpperCase();
  if (!tricode || tricode.length !== 3) {
    return '';
  }
  return `https://assets.nhle.com/logos/nhl/svg/${tricode}_dark.svg`;
};

const fetchWithTimeout = async (input: RequestInfo | URL, init: RequestInit = {}) => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    return await fetch(input, {
      ...init,
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeout);
  }
};

const scrollYourPathToBottom = async () => {
  await nextTick();
  const container = yourPathScrollRef.value;
  if (!container) {
    return;
  }
  container.scrollTop = container.scrollHeight;
};

const startGame = async () => {
  loading.value = true;
  errorBanner.value = null;
  statusMessage.value = 'Starting a new game...';

  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/game/path/start`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Failed to start game');
    }

    const data = await response.json();
    sessionId.value = data.session_id;
    startPlayer.value = data.start_player;
    endPlayer.value = data.end_player;
    currentPath.value = data.current_path;
    pathConnections.value = [];
    completed.value = data.completed;
    gaveUp.value = false;
    optimalPath.value = [];
    optimalConnections.value = [];
    shortestPathLength.value = 0;
    statusMessage.value = 'Game started. Pick a teammate connected to your current path end.';
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      errorBanner.value = 'Request timed out while starting game. Check backend logs and try again.';
      statusMessage.value = 'Start request timed out.';
    } else if (error instanceof TypeError) {
      errorBanner.value = 'Network error reaching backend. Ensure API server is running on port 8000.';
      statusMessage.value = 'Start request failed before reaching backend.';
    } else {
      errorBanner.value = 'Could not start a game session. Please try again.';
      statusMessage.value = 'Start request failed.';
    }
  } finally {
    loading.value = false;
  }
};

const submitGuess = async (player: SearchPlayer) => {
  if (!sessionId.value || completed.value || gaveUp.value || loading.value) {
    return;
  }

  loading.value = true;
  errorBanner.value = null;
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/game/path/guess`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId.value,
        player_id: player.id,
      }),
    });
    if (!response.ok) {
      throw new Error('Failed to submit guess');
    }

    const data = await response.json();
    currentPath.value = data.current_path;
    completed.value = data.completed;
    statusMessage.value = data.message;

    if (data.valid && Array.isArray(data.last_step_teams) && data.last_step_teams.length > 0) {
      const mappedConnections = data.last_step_teams.map((teamLabel: string) => ({
        teamName: teamLabel,
        numStrikes: 0,
        teamLogoURL: getTeamLogoFromLabel(teamLabel),
      }));
      pathConnections.value.push(mappedConnections);
      await scrollYourPathToBottom();
    }

    if (!data.valid) {
      popupCounter.value += 1;
      const popupId = popupCounter.value;
      noLinkPopups.value.push({
        id: popupId,
        playerName: player.full_name,
      });
      setTimeout(() => {
        noLinkPopups.value = noLinkPopups.value.filter((entry) => entry.id !== popupId);
      }, 2200);
    }
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      errorBanner.value = 'Guess request timed out. Backend may still be processing.';
      statusMessage.value = 'Guess request timed out.';
    } else if (error instanceof TypeError) {
      errorBanner.value = 'Network error reaching backend while submitting guess.';
      statusMessage.value = 'Guess request failed before reaching backend.';
    } else {
      errorBanner.value = 'Could not submit guess. Please try again.';
      statusMessage.value = 'Guess request failed.';
    }
  } finally {
    loading.value = false;
  }
};

const giveUp = () => {
  if (!sessionId.value || completed.value || gaveUp.value) {
    return;
  }
  gaveUp.value = true;
  statusMessage.value = 'You gave up. Guessing is disabled. You can now view the optimal solution.';
};

const showOptimalSolution = async () => {
  if (!sessionId.value || loading.value) {
    return;
  }

  loading.value = true;
  errorBanner.value = null;
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/game/path/${sessionId.value}/optimal`);
    if (!response.ok) {
      throw new Error('Failed to load optimal solution');
    }

    const data = await response.json();
    optimalPath.value = data.shortest_path;
    shortestPathLength.value = data.shortest_path_length;
    optimalConnections.value = Array.isArray(data.optimal_step_teams)
      ? data.optimal_step_teams.map((stepLinks: string[]) =>
          stepLinks.map((teamLabel: string) => ({
            teamName: teamLabel,
            numStrikes: 0,
            teamLogoURL: getTeamLogoFromLabel(teamLabel),
          })),
        )
      : [];
    statusMessage.value = 'Optimal solution loaded.';
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      errorBanner.value = 'Optimal solution request timed out.';
      statusMessage.value = 'Optimal request timed out.';
    } else if (error instanceof TypeError) {
      errorBanner.value = 'Network error reaching backend while loading optimal solution.';
      statusMessage.value = 'Optimal request failed before reaching backend.';
    } else {
      errorBanner.value = 'Could not load optimal solution. Please try again.';
      statusMessage.value = 'Optimal request failed.';
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style lang="postcss" scoped>
.home-view {
  @apply mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-4 p-4 text-white;

  .subtitle {
    @apply text-sm text-slate-300;
  }

  .controls {
    @apply flex flex-wrap gap-2;
  }

  .action-btn {
    @apply rounded bg-emerald-600 px-4 py-2 font-semibold text-white;

    &:disabled {
      @apply cursor-not-allowed bg-slate-500;
    }

    &.secondary {
      @apply bg-blue-600;
    }

    &.danger {
      @apply bg-red-700;
    }
  }

  .status {
    @apply rounded bg-slate-800 p-3;
  }

  .error-banner {
    @apply rounded border border-red-300 bg-red-900/50 p-3 text-red-100;
  }

  .no-link-popups {
    @apply absolute left-1/2 top-10 z-20 w-[min(520px,90%)] -translate-x-1/2 flex flex-col gap-2;
  }

  .targets {
    @apply grid gap-3 md:grid-cols-2;
  }

  .target-card {
    @apply rounded bg-slate-800 p-3;
  }

  .path-section,
  .guess-section,
  .optimal-section {
    @apply rounded bg-slate-800 p-3;

    ol {
      @apply ml-4 list-decimal;
    }
  }

  .path-section {
    @apply relative;
  }

  .path-visual-scroll {
    @apply mt-2 flex max-h-[420px] flex-col gap-2 overflow-y-auto pr-1;

    .path-node {
      @apply flex flex-col items-center gap-2;
    }

    .path-player-card {
      @apply w-full max-w-[420px] mx-auto;
    }

    .path-connection {
      @apply flex w-full max-w-[420px] mx-auto flex-col items-center gap-1;
    }

    .path-arrow {
      @apply text-xl text-slate-300;
    }
  }
}
</style>
