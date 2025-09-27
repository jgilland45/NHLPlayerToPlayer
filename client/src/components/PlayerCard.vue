<template>
    <div class="player-card-container">
        <div class="photo-card">
            <img
                class="photo-card-img"
                :src="playerImageURL"
                @error="imageLoadError"
            />
        </div>
        <div class="info">
            {{ playerName }}
        </div>
    </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
    playerImageURL?: string,
    playerName: string,
}>(), {
    playerImageURL: "",
});

const imageLoadError = (e: any) => {
    e.target.src = "https://assets.nhle.com/mugs/nhl/default-skater.png"
}
</script>
  
<style scoped lang="postcss">
.player-card-container {
    @apply flex flex-auto justify-start items-center flex-row w-full border-2 border-solid border-black gap-3 cursor-pointer bg-gray-800 max-h-[120px];
    &:hover {
        @apply bg-gray-600;
    }
    .photo-card {
        @apply flex w-[100px];
        .photo-card-img {
            @apply h-full w-full;
        }
    }
    .info {
        @apply flex text-xl;
    }
}
</style>
  