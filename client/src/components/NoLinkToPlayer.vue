<template>
    <div class="no-link-to-player-container">
        <div class="strike-icon">
            <Icon icon="line-md:close" />
        </div>
        <div class="player-not-link">
            <template v-if="reason">
                <span class="player-name">{{ playerName }}</span> is invalid: {{ reason }}
            </template>
            <template v-else>
                <span class="player-name">{{ playerName }}</span> is not a valid link!
            </template>
        </div>
    </div>
</template>

<script setup lang="ts">
import { Icon } from "@iconify/vue";

defineProps<{
    playerName: string,
    reason?: string,
}>();
</script>
  
<style scoped lang="postcss">
.no-link-to-player-container {
    @apply flex flex-row flex-auto justify-start items-center w-full border-2 border-solid border-red-800 gap-2 min-h-[52px] p-3 rounded bg-red-700 text-white shadow-lg;
    .player-not-link {
        @apply flex text-base leading-snug;
        .player-name {
            @apply font-bold;
        }
    }
    .strike-icon {
        @apply flex items-center text-white text-2xl;
    }
}
</style>
  
