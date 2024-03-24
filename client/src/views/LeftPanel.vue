<template>
    <div
        class="left-panel-container"
        :class="{ small: smallPanel }"
    >
        <div
            class="hamburger-icon"
            @click="() => setPanelSize()"
        >
            <Icon
                icon="ci:hamburger-lg"
                :width="'100%'"
                :height="'100%'"
            />
        </div>
        <div
            class="buttons"
        >
            <ButtonLink
                :show-icon="smallPanel"
                :icon="'ic:baseline-home'"
                :label="'Home'"
                :link="'/'"
            />
            <ButtonLink
                :show-icon="smallPanel"
                :icon="'ph:sun-fill'"
                :label="'Single Player Daily'"
                :link="'/single-player/daily'"
            />
            <ButtonLink
                :show-icon="smallPanel"
                :icon="'ph:infinity-bold'"
                :label="'Single Player Unlimited'"
                :link="'/'"
            />
            <ButtonLink
                :show-icon="smallPanel"
                :icon="'material-symbols:swords'"
                :label="'Online Battles'"
                :link="'/'"
            />
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import ButtonLink from '@/components/ButtonLink.vue'
import { Icon } from '@iconify/vue'

const smallPanel = ref(true)

const setPanelSize = () => {
    smallPanel.value = !smallPanel.value
}

</script>

<style lang="postcss" scoped>
.left-panel-container {
    @apply bg-[#1a1a1a] h-full w-[10%] min-w-12;

    &.small {
        @apply w-[3%];
    }

    .hamburger-icon {
        @apply text-white w-10 ml-2 my-3 cursor-pointer;
    }

    .buttons {
        @apply flex flex-col gap-5 justify-start items-center w-full mt-10;
    }
}
</style>
