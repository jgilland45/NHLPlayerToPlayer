<template>
  <main class="multiplayer-home">
    <div class="top-row">
      <RouterLink
        class="back-link"
        to="/"
      >
        Back to Menu
      </RouterLink>
    </div>

    <h1>Two-Player Lobby</h1>
    <p class="subtitle">Create a lobby and share the code, or join with a code you received.</p>

    <section class="card">
      <h2>Create Lobby</h2>
      <button
        class="action-btn"
        :disabled="creatingLobby"
        @click="createLobby"
      >
        {{ creatingLobby ? 'Creating...' : 'Create Lobby' }}
      </button>
    </section>

    <section class="card">
      <h2>Join Lobby</h2>
      <div class="join-controls">
        <input
          v-model="joinCode"
          class="code-input"
          maxlength="6"
          placeholder="Enter code"
          @keyup.enter="goToLobby"
        >
        <button
          class="action-btn secondary"
          @click="goToLobby"
        >
          Join Lobby
        </button>
      </div>
    </section>

    <p
      v-if="errorBanner"
      class="error-banner"
    >
      {{ errorBanner }}
    </p>
  </main>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { RouterLink, useRouter } from 'vue-router';

const router = useRouter();
const API_BASE_URL = import.meta.env.DEV ? '/api' : 'http://127.0.0.1:8000';
const REQUEST_TIMEOUT_MS = 15000;
const CREATE_LOBBY_REQUEST_TIMEOUT_MS = 60000;

const creatingLobby = ref(false);
const joinCode = ref('');
const errorBanner = ref<string | null>(null);

const normalizedJoinCode = computed(() => joinCode.value.trim().toUpperCase());

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

const createLobby = async () => {
  creatingLobby.value = true;
  errorBanner.value = null;
  try {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/game/multiplayer/lobbies`,
      {
        method: 'POST',
      },
      CREATE_LOBBY_REQUEST_TIMEOUT_MS,
    );
    if (!response.ok) {
      throw new Error('Failed to create lobby');
    }

    const data = await response.json();
    const code = String(data.code ?? '').toUpperCase();
    const creatorToken = String(data.creator_token ?? '');
    if (!code) {
      throw new Error('Created lobby is missing a code');
    }
    if (creatorToken) {
      localStorage.setItem(`nhl-player-to-player-creator-token-${code}`, creatorToken);
    }
    await router.push(`/multiplayer/${code}`);
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      errorBanner.value = 'Create lobby request timed out.';
    } else {
      errorBanner.value = 'Could not create lobby. Please try again.';
    }
  } finally {
    creatingLobby.value = false;
  }
};

const goToLobby = async () => {
  errorBanner.value = null;
  if (normalizedJoinCode.value.length !== 6) {
    errorBanner.value = 'Lobby code must be 6 characters.';
    return;
  }
  await router.push(`/multiplayer/${normalizedJoinCode.value}`);
};
</script>

<style scoped lang="postcss">
.multiplayer-home {
  @apply mx-auto flex min-h-screen w-full max-w-3xl flex-col gap-4 px-4 py-8 text-white;

  .top-row {
    @apply flex;

    .back-link {
      @apply text-sm text-slate-300 no-underline hover:text-white;
    }
  }

  .subtitle {
    @apply text-sm text-slate-300;
  }

  .card {
    @apply rounded-lg bg-slate-800 p-4;

    h2 {
      @apply mb-3 text-lg font-semibold;
    }
  }

  .join-controls {
    @apply flex flex-col gap-2 sm:flex-row;
  }

  .code-input {
    @apply w-full rounded border border-slate-600 bg-slate-900 px-3 py-2 font-mono uppercase tracking-wider text-white;
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

  .error-banner {
    @apply rounded border border-red-300 bg-red-900/50 p-3 text-red-100;
  }
}
</style>
