<template>
    <div class="team-connections-bundle-container">
        <TeamConnections
            v-for="connection in teamConnections"
            :num-strikes="connection.numStrikes"
            :team-name="connection.teamName"
            :team-logo-u-r-l="connection.teamLogoURL ?? ''"
        />
    </div>
</template>

<script setup lang="ts">
import TeamConnections from '@/components/TeamConnections.vue';

export type TeamConnection = {
    teamName: string,
    numStrikes: number,
    teamLogoURL?: string,
}

defineProps<{
    teamConnections: TeamConnection[]
}>();
</script>
  
<style scoped lang="postcss">
.team-connections-bundle-container {
    @apply flex flex-col justify-start items-center max-h-[120px] overflow-y-auto gap-1 p-2 h-full w-full;
}
</style>
  