<template>
    <div
        class="simple-search-container"
    >
        <div class="icon-container">
            <Icon icon="material-symbols:search" />
        </div>
        <input
            :aria-label="placeholderText"
            type="text"
            class="search-input"
            :placeholder="placeholderText"
            v-model="text"
        >
    </div>
</template>

<script setup lang="ts">
import { Icon } from '@iconify/vue';

withDefaults(defineProps<{
    placeholderText?: string,
}>(), {
    placeholderText: 'Search for a teammate',
});

const text = defineModel<string>();
</script>

<style lang="postcss" scoped>
.simple-search-container {
    @apply flex flex-row gap-2 relative w-full;
    .icon-container {
        @apply absolute left-3 top-0 h-full flex items-center text-slate-600;
    }
    .search-input {
        @apply w-full py-2 pr-3 pl-10 border rounded-sm text-slate-900 font-semibold text-base caret-blue-500;
        @apply text-ellipsis;
        &::placeholder {
            @apply text-slate-600 font-normal;
        }
    }
}
</style>
