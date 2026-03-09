<template>
    <div class="team-connections-container">
        <div class="link-icon">
            <Icon icon="line-md:link" />
        </div>
        <div class="team-name">
            {{ teamName }}
        </div>
        <div class="team-logo">
            <img
                class="team-logo-img"
                :src="teamLogoURL"
                @error="imageLoadError"
            />
        </div>
        <div class="strikes">
            <div class="strikes-icons">
                <Icon class="strike-icon" icon="line-md:close" v-for="strike in Array(numStrikes).keys()" />
                <Icon class="no-strike-icon" icon="line-md:close" v-for="strike in Array(3 - numStrikes).keys()" />
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { Icon } from "@iconify/vue";

withDefaults(defineProps<{
    teamName: string,
    numStrikes: number,
    teamLogoURL?: string,
}>(), {
    teamLogoURL: "",
});

const imageLoadError = (e: any) => {
    e.target.src = "https://www.nhl.com/assets/icons/fav/nhl/favicon-apple-touch-icon.png"
}
</script>
  
<style scoped lang="postcss">
.team-connections-container {
    @apply flex flex-row items-center w-full border-2 border-solid border-black gap-1 h-[26px] px-1;
    .link-icon {
        @apply flex items-center justify-center w-[20px] min-w-[20px];
    }
    .team-name {
        @apply flex text-[11px] leading-none whitespace-nowrap overflow-hidden text-ellipsis;
    }
    .team-logo {
        @apply w-[18px] h-[18px] min-w-[18px] min-h-[18px];
        .team-logo-img {
            @apply h-full w-full;
        }
    }
    .strikes {
        @apply flex ml-auto pl-1;
        .strikes-icons {
            @apply flex flex-row justify-center items-center;
            .strike-icon {
                @apply text-red-700;
            }
            .no-strike-icon {
                @apply text-black;
            }
        }
    }
}
</style>
  