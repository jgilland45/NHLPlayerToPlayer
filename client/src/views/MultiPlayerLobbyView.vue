<template>
  <main class="lobby-view">
    <div class="top-row">
      <RouterLink
        class="back-link"
        to="/multiplayer"
      >
        Back
      </RouterLink>
    </div>

    <section class="lobby-header">
      <h1>Lobby {{ lobbyCode }}</h1>
      <div class="share-row">
        <p class="share-url">
          {{ lobbyUrl }}
        </p>
        <button
          class="action-btn secondary"
          @click="copyLobbyUrl"
        >
          Copy URL
        </button>
      </div>
    </section>

    <section class="panel">
      <h2>Players</h2>
      <ul class="player-list">
        <li
          v-for="player in orderedPlayers"
          :key="player.name"
          class="player-row"
        >
          <div class="player-row-main">
            <strong>{{ player.name }}</strong>
            <span
              v-if="player.is_you"
              class="you-badge"
            >
              You
            </span>
          </div>
          <span
            v-if="state?.status === 'in_progress' && state.active_player_name === player.name && !state.game_over"
            class="timer"
          >
            {{ activeTimerSeconds }}s
          </span>
        </li>
      </ul>
      <p class="rules-note">
        Team-season links can only be used {{ state?.connection_cap ?? 3 }} times each.
      </p>
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2>Game Settings</h2>
        <button
          class="action-btn secondary"
          :disabled="!canEditSettings || settingsLoading || savingSettings"
          @click="openSettingsModal"
        >
          {{ settingsLoading ? 'Loading...' : 'Edit Settings' }}
        </button>
      </div>
      <p class="subtitle">
        Game types: {{ state?.settings.game_types.length ?? 0 }} selected
      </p>
      <p class="subtitle">
        Teams: {{ state && state.settings.teams.length === 0 ? 'All teams' : `${state?.settings.teams.length ?? 0} selected` }}
      </p>
      <p class="subtitle">
        Season range: {{ state?.settings.start_year ?? '-' }} to {{ state?.settings.end_year ?? '-' }}
      </p>
      <p
        v-if="!state?.is_joined"
        class="subtitle"
      >
        Join the lobby to edit settings.
      </p>
      <p
        v-else-if="!canEditSettings"
        class="subtitle"
      >
        Only the lobby creator can edit settings.
      </p>
    </section>

    <section
      v-if="!state?.is_joined"
      class="panel"
    >
      <h2>Join This Game</h2>
      <p class="subtitle">
        This lobby supports exactly two players.
      </p>

      <button
        v-if="!showJoinForm"
        class="action-btn"
        @click="showJoinForm = true"
      >
        Join game
      </button>

      <div
        v-else
        class="join-form"
      >
        <input
          v-model="joinName"
          class="name-input"
          maxlength="24"
          placeholder="Your name"
          @keyup.enter="joinGame"
        >
        <button
          class="action-btn"
          :disabled="joining"
          @click="joinGame"
        >
          {{ joining ? 'Joining...' : 'Confirm Join' }}
        </button>
      </div>
    </section>

    <section
      v-if="state?.is_joined && state.status === 'waiting_for_player'"
      class="panel"
    >
      <h2>Waiting For Player 2</h2>
      <p>Share the lobby URL and wait for them to join. The game auto-starts at 2 players.</p>
    </section>

    <section
      v-if="state?.is_joined && state.status === 'in_progress' && !state.game_over"
      class="panel turn-panel"
    >
      <h2>Current Turn</h2>
      <p v-if="state.is_your_turn">
        Your turn. {{ activeTimerSeconds }} seconds left.
      </p>
      <p v-else>
        Waiting for {{ state.active_player_name }}. {{ activeTimerSeconds }} seconds left.
      </p>
    </section>

    <section
      v-if="state?.game_over"
      class="panel game-over-panel"
    >
      <h2>Game Over</h2>
      <p class="winner-line">
        Winner: <strong>{{ state.winner_name }}</strong>
      </p>
      <p>
        {{ state.loser_name }} ran out of time.
      </p>
      <button
        class="action-btn"
        :disabled="playingAgain"
        @click="playAgain"
      >
        {{ playingAgain ? 'Starting...' : 'Play Again' }}
      </button>
    </section>

    <section
      v-if="state?.is_joined && state.status === 'in_progress' && !state.game_over"
      class="panel"
    >
      <h2>Guess A Teammate</h2>
      <p
        v-if="!state.is_your_turn"
        class="subtitle"
      >
        You can guess only on your turn.
      </p>
      <SearchWithResults
        v-else
        @click="submitGuess"
      />
    </section>

    <section
      v-if="state?.current_path?.length"
      class="panel path-panel"
    >
      <h2>Path</h2>

      <div
        v-if="noLinkPopups.length"
        class="no-link-popups"
      >
        <NoLinkToPlayer
          v-for="popup in noLinkPopups"
          :key="popup.id"
          :player-name="popup.playerName"
          :reason="popup.reason"
        />
      </div>

      <div
        ref="pathScrollRef"
        class="path-visual-scroll"
      >
        <div
          v-for="(player, index) in state.current_path"
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

    <GameSettingsModal
      :open="settingsOpen"
      :options="settingsOptions"
      :initial-settings="modalInitialSettings"
      :saving="savingSettings"
      title="Multiplayer Settings"
      @close="settingsOpen = false"
      @save="saveLobbySettings"
    />
  </main>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';

import GameSettingsModal from '@/components/GameSettingsModal.vue';
import NoLinkToPlayer from '@/components/NoLinkToPlayer.vue';
import PlayerCard from '@/components/PlayerCard.vue';
import SearchWithResults, { type Player as SearchPlayer } from '@/components/SearchWithResults.vue';
import TeamConnectionBundle, { type TeamConnection } from '@/components/TeamConnectionBundle.vue';
import type {
  ConnectionSettings,
  ConnectionSettingsOptions,
  ConnectionSettingsOptionsResponse,
} from '@/types/gameSettings';

type ApiPlayer = {
  id: number;
  full_name: string;
};

type LobbyPlayer = {
  name: string;
  is_you: boolean;
};

type LobbyState = {
  code: string;
  status: 'waiting_for_player' | 'in_progress' | 'game_over';
  max_players: number;
  turn_seconds: number;
  connection_cap: number;
  players: LobbyPlayer[];
  you_name: string | null;
  is_joined: boolean;
  settings: ConnectionSettings;
  current_path: ApiPlayer[];
  step_teams: string[][];
  team_usage: Record<string, number>;
  active_player_name: string | null;
  is_your_turn: boolean;
  turn_deadline_epoch_ms: number | null;
  active_turn_remaining_ms: number;
  game_over: boolean;
  winner_name: string | null;
  loser_name: string | null;
  end_reason: string | null;
};

type PopupEntry = {
  id: number;
  playerName: string;
  reason: string;
};

type TeamMeta = {
  teamName: string;
  teamLogoURL: string;
};

const route = useRoute();
const API_BASE_URL = import.meta.env.DEV ? '/api' : 'http://127.0.0.1:8000';
const REQUEST_TIMEOUT_MS = 15000;
const SETTINGS_REQUEST_TIMEOUT_MS = 60000;

const state = ref<LobbyState | null>(null);
const playerToken = ref<string | null>(null);
const creatorToken = ref<string | null>(null);
const joinName = ref('');
const showJoinForm = ref(false);
const joining = ref(false);
const playingAgain = ref(false);
const statusMessage = ref('Press "Join game" to join this lobby.');
const errorBanner = ref<string | null>(null);
const countdownMs = ref(0);
const pathConnections = ref<TeamConnection[][]>([]);
const noLinkPopups = ref<PopupEntry[]>([]);
const popupCounter = ref(0);
const pathScrollRef = ref<HTMLElement | null>(null);
const settingsOptions = ref<ConnectionSettingsOptions | null>(null);
const settingsLoading = ref(false);
const settingsOpen = ref(false);
const savingSettings = ref(false);
const modalInitialSettings = ref<ConnectionSettings | null>(null);

const teamMetaCache = new Map<string, Promise<TeamMeta>>();
let pollIntervalId: number | null = null;
let countdownIntervalId: number | null = null;
let connectionsBuildSequence = 0;

const lobbyCode = computed(() => String(route.params.code ?? '').trim().toUpperCase());
const lobbyUrl = computed(() => `${window.location.origin}/multiplayer/${lobbyCode.value}`);
const tokenStorageKey = computed(() => `nhl-player-to-player-token-${lobbyCode.value}`);
const nameStorageKey = computed(() => `nhl-player-to-player-name-${lobbyCode.value}`);
const creatorTokenStorageKey = computed(() => `nhl-player-to-player-creator-token-${lobbyCode.value}`);
const orderedPlayers = computed(() => state.value?.players ?? []);
const activeTimerSeconds = computed(() => Math.ceil(countdownMs.value / 1000));
const canEditSettings = computed(() => Boolean(state.value?.is_joined && creatorToken.value));

const getPlayerImage = (playerId: number) => `https://assets.nhle.com/mugs/nhl/latest/${playerId}.png`;

const cloneSettings = (settings: ConnectionSettings): ConnectionSettings => ({
  game_types: [...settings.game_types],
  teams: [...settings.teams],
  start_year: Number(settings.start_year),
  end_year: Number(settings.end_year),
});

const fetchWithTimeout = async (
  input: RequestInfo | URL,
  init: RequestInit = {},
  timeoutMs: number = REQUEST_TIMEOUT_MS,
) => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(input, {
      ...init,
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeout);
  }
};

const readErrorMessage = async (response: Response): Promise<string> => {
  try {
    const body = await response.json();
    if (typeof body?.detail === 'string' && body.detail.trim()) {
      return body.detail;
    }
  } catch {
    // Ignore parse failures and use generic status text.
  }
  return `Request failed (${response.status}).`;
};

const loadSettingsOptions = async () => {
  if (settingsLoading.value) {
    return;
  }
  settingsLoading.value = true;
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/game/multiplayer/settings`, {}, SETTINGS_REQUEST_TIMEOUT_MS);
    if (!response.ok) {
      throw new Error(await readErrorMessage(response));
    }
    const data = (await response.json()) as ConnectionSettingsOptionsResponse;
    settingsOptions.value = data.options;
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error('Loading game settings timed out. Please try again.');
    }
    throw error;
  } finally {
    settingsLoading.value = false;
  }
};

const openSettingsModal = async () => {
  if (!canEditSettings.value) {
    errorBanner.value = 'Only the lobby creator can edit game settings.';
    return;
  }
  errorBanner.value = null;
  try {
    if (!settingsOptions.value) {
      await loadSettingsOptions();
    }
    modalInitialSettings.value = state.value?.settings ? cloneSettings(state.value.settings) : null;
    settingsOpen.value = true;
  } catch (error) {
    errorBanner.value = error instanceof Error ? error.message : 'Could not load settings.';
  }
};

const saveLobbySettings = async (nextSettings: ConnectionSettings) => {
  if (!playerToken.value) {
    errorBanner.value = 'Join the lobby before changing settings.';
    return;
  }
  if (!creatorToken.value) {
    errorBanner.value = 'Only the lobby creator can change settings.';
    return;
  }

  savingSettings.value = true;
  errorBanner.value = null;
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/game/multiplayer/lobbies/${lobbyCode.value}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_token: playerToken.value,
        creator_token: creatorToken.value,
        settings: cloneSettings(nextSettings),
      }),
    });
    if (!response.ok) {
      throw new Error(await readErrorMessage(response));
    }
    const data = await response.json();
    settingsOpen.value = false;
    statusMessage.value = 'Game settings updated.';
    await updateStateFromResponse(data.state as LobbyState);
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      errorBanner.value = 'Settings update request timed out.';
    } else {
      errorBanner.value = error instanceof Error ? error.message : 'Could not update settings.';
    }
  } finally {
    savingSettings.value = false;
  }
};

const loadStoredIdentity = () => {
  playerToken.value = localStorage.getItem(tokenStorageKey.value);
  const storedName = localStorage.getItem(nameStorageKey.value);
  if (storedName) {
    joinName.value = storedName;
  }
};

const loadStoredCreatorToken = () => {
  creatorToken.value = localStorage.getItem(creatorTokenStorageKey.value);
};

const persistIdentity = (token: string, playerName: string) => {
  playerToken.value = token;
  joinName.value = playerName;
  localStorage.setItem(tokenStorageKey.value, token);
  localStorage.setItem(nameStorageKey.value, playerName);
};

const clearIdentity = () => {
  playerToken.value = null;
  localStorage.removeItem(tokenStorageKey.value);
  localStorage.removeItem(nameStorageKey.value);
};

const normalizeSeasonToEightDigits = (seasonText: string): string => {
  const raw = seasonText.trim();
  if (/^\d{8}$/.test(raw)) {
    return raw;
  }
  const seasonMatch = raw.match(/^(\d{4})-(\d{2})$/);
  if (!seasonMatch) {
    return '';
  }
  const startYear = seasonMatch[1];
  const endYearShort = seasonMatch[2];
  const centuryPrefix = startYear.slice(0, 2);
  return `${startYear}${centuryPrefix}${endYearShort}`;
};

const getTeamSeasonSortValue = (teamLabel: string): number => {
  const [, seasonRaw = ''] = teamLabel.trim().split(' ');
  const normalized = normalizeSeasonToEightDigits(seasonRaw);
  if (normalized.length === 8) {
    return Number(normalized.slice(0, 4));
  }
  const seasonMatch = seasonRaw.match(/^(\d{4})-(\d{2})$/);
  if (seasonMatch) {
    return Number(seasonMatch[1]);
  }
  return 0;
};

const getTeamMeta = async (teamLabel: string): Promise<TeamMeta> => {
  const [triCodeRaw, seasonRaw] = teamLabel.trim().split(' ');
  const triCode = (triCodeRaw ?? '').toUpperCase();
  const years = normalizeSeasonToEightDigits(seasonRaw ?? '');

  if (triCode.length !== 3 || years.length !== 8) {
    return {
      teamName: teamLabel,
      teamLogoURL: `https://assets.nhle.com/logos/nhl/svg/${triCode || 'NHL'}_dark.svg`,
    };
  }

  let logo = `https://assets.nhle.com/logos/nhl/svg/${triCode}_dark.svg`;
  let name = triCode;
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/team/logo?team_tricode=${triCode}&year=${years}`);
    if (response.ok) {
      const data = await response.json();
      if (typeof data?.logo === 'string' && data.logo.length > 0) {
        logo = data.logo;
      }
      if (typeof data?.name === 'string' && data.name.length > 0) {
        name = data.name;
      }
    }
  } catch {
    // Use fallback logo/name when team API is unavailable.
  }

  return {
    teamName: `${name} ${years.slice(0, 4)}-${years.slice(6, 8)}`,
    teamLogoURL: logo,
  };
};

const rebuildPathConnections = async (nextState: LobbyState | null) => {
  const currentSequence = ++connectionsBuildSequence;
  if (!nextState) {
    pathConnections.value = [];
    return;
  }

  const usageMap = nextState.team_usage ?? {};
  const mappedConnections = await Promise.all(
    (nextState.step_teams ?? []).map(async (stepTeamLabels) => {
      const sortedStepTeamLabels = [...stepTeamLabels].sort((left, right) => {
        const usageDiff = (usageMap[right] ?? 0) - (usageMap[left] ?? 0);
        if (usageDiff !== 0) {
          return usageDiff;
        }
        const seasonDiff = getTeamSeasonSortValue(right) - getTeamSeasonSortValue(left);
        if (seasonDiff !== 0) {
          return seasonDiff;
        }
        return left.localeCompare(right);
      });

      return Promise.all(sortedStepTeamLabels.map(async (teamLabel) => {
        if (!teamMetaCache.has(teamLabel)) {
          teamMetaCache.set(teamLabel, getTeamMeta(teamLabel));
        }
        const teamMeta = await teamMetaCache.get(teamLabel)!;
        return {
          teamName: teamMeta.teamName,
          numStrikes: Math.min(usageMap[teamLabel] ?? 0, nextState.connection_cap),
          teamLogoURL: teamMeta.teamLogoURL,
        };
      }));
    }),
  );

  if (currentSequence === connectionsBuildSequence) {
    pathConnections.value = mappedConnections;
  }
};

const scrollPathToBottom = async () => {
  await nextTick();
  const container = pathScrollRef.value;
  if (!container) {
    return;
  }
  container.scrollTop = container.scrollHeight;
};

const updateCountdown = () => {
  if (!state.value || state.value.status !== 'in_progress' || state.value.game_over || !state.value.turn_deadline_epoch_ms) {
    countdownMs.value = 0;
    return;
  }
  countdownMs.value = Math.max(state.value.turn_deadline_epoch_ms - Date.now(), 0);
};

const updateStateFromResponse = async (nextState: LobbyState) => {
  const previousPathLength = state.value?.current_path?.length ?? 0;
  const previousStepCount = state.value?.step_teams?.length ?? 0;
  state.value = nextState;
  await rebuildPathConnections(nextState);
  updateCountdown();
  const hasNewPathNode = (nextState.current_path?.length ?? 0) > previousPathLength;
  const hasNewStep = (nextState.step_teams?.length ?? 0) > previousStepCount;
  if (hasNewPathNode || hasNewStep) {
    await scrollPathToBottom();
  }

  if (playerToken.value && !nextState.is_joined) {
    clearIdentity();
    showJoinForm.value = true;
  }
};

const refreshState = async () => {
  try {
    const params = new URLSearchParams();
    if (playerToken.value) {
      params.set('player_token', playerToken.value);
    }
    const query = params.toString();
    const url = `${API_BASE_URL}/game/multiplayer/lobbies/${lobbyCode.value}${query ? `?${query}` : ''}`;
    const response = await fetchWithTimeout(url);
    if (!response.ok) {
      throw new Error(await readErrorMessage(response));
    }
    const data = await response.json();
    await updateStateFromResponse(data.state as LobbyState);
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      errorBanner.value = 'Lobby state request timed out.';
      return;
    }
    errorBanner.value = error instanceof Error ? error.message : 'Could not load lobby state.';
  }
};

const joinGame = async () => {
  if (!joinName.value.trim()) {
    errorBanner.value = 'Please enter a name.';
    return;
  }

  joining.value = true;
  errorBanner.value = null;
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/game/multiplayer/lobbies/${lobbyCode.value}/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: joinName.value.trim(),
        player_token: playerToken.value ?? undefined,
      }),
    });
    if (!response.ok) {
      throw new Error(await readErrorMessage(response));
    }

    const data = await response.json();
    persistIdentity(String(data.player_token), String(data.player_name));
    showJoinForm.value = false;
    statusMessage.value = 'Joined lobby successfully.';
    await updateStateFromResponse(data.state as LobbyState);
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      errorBanner.value = 'Join request timed out.';
    } else {
      errorBanner.value = error instanceof Error ? error.message : 'Could not join lobby.';
    }
  } finally {
    joining.value = false;
  }
};

const attemptAutoJoin = async () => {
  if (!playerToken.value || !joinName.value.trim()) {
    return;
  }
  await joinGame();
};

const submitGuess = async (player: SearchPlayer) => {
  if (!state.value || !state.value.is_joined || !state.value.is_your_turn || !playerToken.value || state.value.game_over) {
    return;
  }

  errorBanner.value = null;
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/game/multiplayer/lobbies/${lobbyCode.value}/guess`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_token: playerToken.value,
        player_id: player.id,
      }),
    });
    if (!response.ok) {
      throw new Error(await readErrorMessage(response));
    }

    const data = await response.json();
    statusMessage.value = String(data.message ?? '');
    await updateStateFromResponse(data.state as LobbyState);

    if (!data.valid && typeof data.invalid_player_name === 'string' && data.invalid_player_name.length > 0) {
      const overusedTeamSeasons = Array.isArray(data.overused_team_seasons)
        ? (data.overused_team_seasons as string[])
        : [];
      const invalidReason = typeof data.invalid_reason === 'string'
        ? data.invalid_reason
        : String(data.message ?? 'Invalid guess.');
      const popupReason = overusedTeamSeasons.length > 0
        ? `Overused team-season: ${overusedTeamSeasons.join(', ')}.`
        : invalidReason;

      popupCounter.value += 1;
      const popupId = popupCounter.value;
      noLinkPopups.value.push({
        id: popupId,
        playerName: data.invalid_player_name,
        reason: popupReason,
      });
      setTimeout(() => {
        noLinkPopups.value = noLinkPopups.value.filter((entry) => entry.id !== popupId);
      }, 2200);
    }
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      errorBanner.value = 'Guess request timed out.';
    } else {
      errorBanner.value = error instanceof Error ? error.message : 'Could not submit guess.';
    }
  }
};

const playAgain = async () => {
  if (!playerToken.value) {
    errorBanner.value = 'Join the lobby before starting a new round.';
    return;
  }

  playingAgain.value = true;
  errorBanner.value = null;
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/game/multiplayer/lobbies/${lobbyCode.value}/play-again`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_token: playerToken.value,
      }),
    });
    if (!response.ok) {
      throw new Error(await readErrorMessage(response));
    }
    const data = await response.json();
    statusMessage.value = 'New round started.';
    await updateStateFromResponse(data.state as LobbyState);
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      errorBanner.value = 'Play-again request timed out.';
    } else {
      errorBanner.value = error instanceof Error ? error.message : 'Could not start a new round.';
    }
  } finally {
    playingAgain.value = false;
  }
};

const copyLobbyUrl = async () => {
  try {
    await navigator.clipboard.writeText(lobbyUrl.value);
    statusMessage.value = 'Lobby URL copied.';
  } catch {
    errorBanner.value = 'Could not copy URL from this browser.';
  }
};

const startIntervals = () => {
  stopIntervals();
  pollIntervalId = window.setInterval(() => {
    void refreshState();
  }, 1000);
  countdownIntervalId = window.setInterval(() => {
    updateCountdown();
  }, 250);
};

const stopIntervals = () => {
  if (pollIntervalId !== null) {
    clearInterval(pollIntervalId);
    pollIntervalId = null;
  }
  if (countdownIntervalId !== null) {
    clearInterval(countdownIntervalId);
    countdownIntervalId = null;
  }
};

const initializeLobbyPage = async () => {
  state.value = null;
  pathConnections.value = [];
  noLinkPopups.value = [];
  settingsOpen.value = false;
  showJoinForm.value = false;
  errorBanner.value = null;
  statusMessage.value = 'Press "Join game" to join this lobby.';
  loadStoredIdentity();
  loadStoredCreatorToken();
  if (!settingsOptions.value) {
    try {
      await loadSettingsOptions();
    } catch (error) {
      errorBanner.value = error instanceof Error ? error.message : 'Could not load settings options.';
    }
  }
  await refreshState();
  if (playerToken.value && joinName.value.trim()) {
    await attemptAutoJoin();
  }
  startIntervals();
};

watch(lobbyCode, () => {
  void initializeLobbyPage();
});

watch(
  () => pathConnections.value.length,
  async (nextLength, previousLength) => {
    if (nextLength > previousLength) {
      await scrollPathToBottom();
    }
  },
);

onMounted(() => {
  void initializeLobbyPage();
});

onBeforeUnmount(() => {
  stopIntervals();
});
</script>

<style scoped lang="postcss">
.lobby-view {
  @apply mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-4 px-4 py-6 text-white;

  .top-row {
    @apply flex;
  }

  .back-link {
    @apply text-sm text-slate-300 no-underline hover:text-white;
  }

  .lobby-header {
    @apply rounded bg-slate-800 p-4;

    h1 {
      @apply mb-2 text-2xl font-bold;
    }

    .share-row {
      @apply flex flex-col gap-2 sm:flex-row sm:items-center;
    }

    .share-url {
      @apply overflow-x-auto rounded bg-slate-900 px-3 py-2 font-mono text-sm text-slate-300;
    }
  }

  .panel {
    @apply rounded bg-slate-800 p-4;

    .panel-head {
      @apply mb-2 flex items-center justify-between gap-2;
    }

    h2 {
      @apply mb-2 text-lg font-semibold;
    }

    .subtitle {
      @apply text-sm text-slate-300;
    }
  }

  .player-list {
    @apply flex flex-col gap-2;

    .player-row {
      @apply flex items-center justify-between rounded bg-slate-900 px-3 py-2;

      .player-row-main {
        @apply flex items-center gap-2;
      }

      .you-badge {
        @apply rounded bg-emerald-600 px-2 py-0.5 text-xs;
      }

      .timer {
        @apply rounded bg-red-700 px-2 py-0.5 text-sm font-semibold;
      }
    }
  }

  .rules-note {
    @apply mt-2 text-xs text-slate-400;
  }

  .join-form {
    @apply flex flex-col gap-2 sm:flex-row;

    .name-input {
      @apply w-full rounded border border-slate-600 bg-slate-900 px-3 py-2 text-white;
    }
  }

  .turn-panel {
    @apply border border-emerald-500/40;
  }

  .game-over-panel {
    @apply border border-red-500/50;

    .winner-line {
      @apply mb-1 text-lg;
    }
  }

  .path-panel {
    @apply relative;
  }

  .no-link-popups {
    @apply absolute left-1/2 top-10 z-20 flex w-[min(520px,90%)] -translate-x-1/2 flex-col gap-2;
  }

  .path-visual-scroll {
    @apply mt-2 flex max-h-[420px] flex-col gap-2 overflow-y-auto pr-1;

    .path-node {
      @apply flex flex-col items-center gap-2;
    }

    .path-player-card {
      @apply mx-auto w-full max-w-[420px];
    }

    .path-connection {
      @apply mx-auto flex w-full max-w-[420px] flex-col items-center gap-1;
    }

    .path-arrow {
      @apply text-xl text-slate-300;
    }
  }

  .action-btn {
    @apply rounded bg-emerald-600 px-4 py-2 font-semibold text-white;

    &:disabled {
      @apply cursor-not-allowed bg-slate-500;
    }

    &.secondary {
      @apply bg-blue-600;
    }
  }

  .status {
    @apply rounded bg-slate-800 p-3;
  }

  .error-banner {
    @apply rounded border border-red-300 bg-red-900/50 p-3 text-red-100;
  }
}
</style>
