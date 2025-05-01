<template>
  <RouterView />
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<style lang="postcss">
#app {
  @apply bg-gray-900 w-screen h-screen;
}
</style>
