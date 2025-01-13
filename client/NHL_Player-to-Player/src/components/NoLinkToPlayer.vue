<template>
    <div class="no-link-to-player-container">
        <div class="strike-icon">
            <Icon icon="line-md:close" />
        </div>
        <div class="player-not-link">
            <span class="player-name">{{ playerName }}</span> is not a valid link!
        </div>
    </div>
</template>

<script setup lang="ts">
import { Icon } from "@iconify/vue";

defineProps<{
    playerName: string,
}>();
</script>
  
<style scoped lang="postcss">
.no-link-to-player-container {
    @apply flex flex-row flex-auto justify-start items-center w-full border-2 border-solid border-black gap-1 h-[30px] p-1;
    .player-not-link {
        @apply flex text-base whitespace-pre;
        .player-name {
            @apply font-semibold;
        }
    }
    .strike-icon {
        @apply flex items-center text-red-700;
    }
}
</style>
  