<template>
  <main class="menu-view">
    <h1>Teammate Path Game</h1>
    <p class="subtitle">Choose a mode to play.</p>

    <div class="menu-grid">
      <RouterLink
        class="menu-card"
        to="/singleplayer"
      >
        <h2>Single Player</h2>
        <p>Classic path game with random start and end players.</p>
      </RouterLink>

      <RouterLink
        class="menu-card"
        to="/multiplayer"
      >
        <h2>Multi Player</h2>
        <p>Create or join a 2-player lobby using a shareable code.</p>
      </RouterLink>
    </div>
  </main>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
</script>

<style lang="postcss" scoped>
.menu-view {
  @apply mx-auto flex min-h-screen w-full max-w-4xl flex-col gap-5 px-4 py-8 text-white;

  .subtitle {
    @apply text-slate-300;
  }

  .menu-grid {
    @apply grid gap-4 md:grid-cols-2;
  }

  .menu-card {
    @apply block rounded-xl border border-slate-700 bg-slate-800/80 p-5 no-underline transition-colors;
    @apply hover:border-emerald-400 hover:bg-slate-700;

    h2 {
      @apply mb-2 text-xl font-semibold text-white;
    }

    p {
      @apply text-sm text-slate-300;
    }
  }
}
</style>
