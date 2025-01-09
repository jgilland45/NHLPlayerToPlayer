<template>
    <button
        class="button-link"
        @click="goToLink"
    >
        <div v-if="props.icon && props.showIcon">
            <Icon
                class="icon"
                :icon="props.icon"
                width="30"
                height="30"
            />
        </div>
        <div v-else-if="props.label">
            {{ props.label }}
        </div>
    </button>
</template>

<script setup>
import { defineProps } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'

const router = useRouter()

const props = defineProps({
    showIcon: Boolean,
    label: String,
    link: String,
    icon: String
})

function goToLink () {
    router.push(props.link)
}
</script>

<style lang="postcss" scoped>
.button-link {
    @apply border w-full h-10 bg-[#999999] text-white select-none hover:bg-white hover:text-black;

    .icon {
        @apply m-auto;
    }
}
</style>
