<template>
    <div class="single-player-daily-container">
        <LeftPanel />
        <div v-if="wonGame">
            You win!!
        </div>
        <div class="content-container">
            <div class="playersContainer">
                <div class="reverse-container">
                    <div class="overflow-players">
                        <PlayerBlock
                        class="player start"
                        :player="startingPlayer">
                        </PlayerBlock>
                        <PlayerBlock
                            v-for="player in guessedPlayers"
                            :key="player.URL"
                            :player="player"
                            class="player"
                        >
                        </PlayerBlock>
                    </div>
                </div>
                <PlayerBlock
                    class="player end"
                    :player="endingPlayer">
                </PlayerBlock>
            </div>
            <div class="search-block">
                <form
                    v-on:submit.prevent="onSubmit"
                    id="search"
                    autocomplete="off"
                >
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
    </div>
</template>

<script setup>
import { computed } from 'vue'
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
    @apply flex flex-row justify-center items-center h-screen;
    .content-container {
        @apply flex flex-row flex-1 h-full;
        .playersContainer {
            @apply flex flex-col flex-1 items-center bg-gray-100 py-5;
            /* https://stackoverflow.com/questions/18614301/keep-overflow-div-scrolled-to-bottom-unless-user-scrolls-up */
            /* https://codepen.io/anon/pen/pdrLEZ */
            .reverse-container {
                @apply flex flex-col-reverse w-full overflow-y-auto overflow-x-hidden;
                -ms-overflow-style: none;
                scrollbar-width: none;

                &::-webkit-scrollbar {
                    display: none;
                }
            }
            .overflow-players {
                @apply flex flex-col items-center w-full;
            }
            .player {
                @apply mt-3 pl-1 text-xl border-2 border-black w-[40%] min-w-56 bg-white;
            }
            .start {
                @apply bg-green-500;
            }
            .end {
                @apply bg-red-500;
            }
        }
        .search-block {
            @apply flex flex-col p-2 flex-1 items-center gap-4 bg-gray-100;
            #search {
                @apply text-2xl;
            }
            .search-bar {
                @apply bg-gray-100 border border-black;
            }
        }
    }
}
</style>
