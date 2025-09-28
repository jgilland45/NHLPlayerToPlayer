<template>
  <SearchWithResults 
    @click="printPlayerClicked"
  />
</template>

<script setup lang="ts">
import SearchWithResults from '@/components/SearchWithResults.vue';
import { type Player } from '@/components/SearchWithResults.vue';

const printPlayerClicked = (player: Player) => {
  console.log(player);
}

</script>

<style lang="postcss" scoped>
</style>
