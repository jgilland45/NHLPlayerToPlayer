<template>
  <div class="container">
    <InputSearch class="player_input" v-model:model-value="input" />
    <div
      v-for="result in dropDownResults"
    >
      {{ result }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import InputSearch from './InputSearch.vue';
import { useFuse } from '@vueuse/integrations/useFuse';

const input = ref('Jhon D');

const data = [
  'John Smith',
  'John Doe',
  'Jane Doe',
  'Phillip Green',
  'Peter Brown',
];

const { results } = useFuse(input, data);

const dropDownResults = computed(() => results.value.map(d => d.item));

watch(results, (d) => console.log(d));
</script>

<style scoped lang="postcss">
.container {
  @apply flex flex-col gap-2;
}
</style>