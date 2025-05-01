<template>
  <div class="main_page_container">
    <RouterLink
      class="link_button"
      to="/singleplayer"
    >
      Single Player Game
    </RouterLink>
    <RouterLink
      class="link_button"
      to="/multiplayer"
    >
      Multi Player Game
    </RouterLink>
  </div>
</template>

<script setup lang="ts">
</script>

<style lang="postcss" scoped>
.main_page_container {
  @apply flex flex-col justify-center items-center p-10;

  .link_button {
    @apply text-white;
  }
}
</style>
