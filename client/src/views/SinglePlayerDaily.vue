<template>
  <LeftPanel />
    <div class="single-player-daily-container">
        <div v-if="wonGame">
            You win!!
        </div>
        <button @click="playerToPlayerDailyStore.guessRandomPlayer()">Guess random player</button>
        <div class="playersContainer">
            <PlayerBlock
            class="player start"
            :player="startingPlayer">
            </PlayerBlock>
            <PlayerBlock
                v-for="player in guessedPlayers"
                :key="player"
                :player="player"
                class="player"
            >
            </PlayerBlock>
            <PlayerBlock
                class="player end"
                :player="endingPlayer">
            </PlayerBlock>
        </div>
        <div class="search-block">
            <form v-on:submit.prevent="onSubmit" id="search">
                Search <input name="query" v-model="playerToPlayerDailyStore.searchQuery" class="search-bar">
            </form>
            <SearchBlock
                :data="allPossiblePlayers"
                :columns="gridColumns"
                :filterKey="playerToPlayerDailyStore.searchQuery"
                @choose="playerToPlayerDailyStore.guessPlayer">
            </SearchBlock>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, watchEffect, computed, onMounted } from 'vue'
import { usePlayerToPlayerDailyStore } from '@/stores/playerToPlayerDaily'
import LeftPanel from '@/views/LeftPanel.vue'
import SearchBlock from '@/components/SearchBlock.vue'
import PlayerBlock from '@/components/PlayerBlock.vue'

const playerToPlayerDailyStore = usePlayerToPlayerDailyStore()

const wonGame = computed(() => playerToPlayerDailyStore.wonGame)

const startingPlayer = computed(() => playerToPlayerDailyStore.startingPlayer)
const endingPlayer = computed(() => playerToPlayerDailyStore.endingPlayer)
const allPossiblePlayers = computed(() => playerToPlayerDailyStore.allPossiblePlayers)
const guessedPlayers = computed(() => playerToPlayerDailyStore.guessedPlayers)

const gridColumns = ['URL', 'NAME']

const onSubmit = () => console.log('submitted form')

</script>

<style lang="postcss" scoped>
.single-player-daily-container {
    @apply flex flex-col flex-auto justify-center items-center gap-5;
    .playersContainer {
        @apply flex flex-col flex-auto;
        .player {
            @apply mt-3 pl-1 text-xl border-2 border-black;
        }
        .start {
            @apply bg-green-500;
        }
        .end {
            @apply bg-red-500;
        }
    }
    .search-block {
        @apply border p-2;
        .search-bar {
            @apply bg-gray-100 border border-black;
        }
    }
}
</style>
