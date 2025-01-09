<template>
    <div class="single-player-daily-container">
        <LeftPanel />
        <div
            v-if="wonGame"
            class="won-container"
        >
            <span>You win!!</span>
            <ButtonLink
                class="play-again"
                :label="'Click to play again!'"
                :link="'/single-player/unlimited'"
                @click="resetGame"
            />
        </div>
        <div class="content-container">
            <div class="search-block">
                <SearchBar
                    :searchText="searchInputText"
                    @search="setSearchText"
                />
                <SearchBlock
                    :data="allPossiblePlayers"
                    :filterKey="searchInputText"
                    @choose="playerToPlayerUnlimitedStore.guessPlayer">
                </SearchBlock>
            </div>
            <div class="players-container">
                <div
                    ref="scrollRef"
                    class="scrolling-players"
                >
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
                <PlayerBlock
                    class="player end"
                    :player="endingPlayer">
                </PlayerBlock>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { usePlayerToPlayerUnlimitedStore } from '@/stores/playerToPlayerUnlimited'
import LeftPanel from '@/views/LeftPanel.vue'
import SearchBlock from '@/components/SearchBlock.vue'
import PlayerBlock from '@/components/PlayerBlock.vue'
import ButtonLink from '@/components/ButtonLink.vue'
import SearchBar from '@/components/SearchBar.vue'
import { useScroll, useElementBounding } from '@vueuse/core'

const scrollRef = ref()

const { x: scrollX, y: scrollY, arrivedState } = useScroll(scrollRef)
const { x: myX } = useElementBounding(scrollRef)

const playerToPlayerUnlimitedStore = usePlayerToPlayerUnlimitedStore()

const wonGame = computed(() => playerToPlayerUnlimitedStore.wonGame)

const startingPlayer = computed(() => playerToPlayerUnlimitedStore.startingPlayer)
const endingPlayer = computed(() => playerToPlayerUnlimitedStore.endingPlayer)
const allPossiblePlayers = computed(() => playerToPlayerUnlimitedStore.allPossiblePlayers)
const guessedPlayers = computed(() => playerToPlayerUnlimitedStore.guessedPlayers)

const resetGame = computed(() => playerToPlayerUnlimitedStore.resetGame)
const resetSearch = computed(() => playerToPlayerUnlimitedStore.resetSearch)

const searchInputText = ref('')

const setSearchText = (inputText) => {
    searchInputText.value = inputText
}

watch(resetSearch, () => {
    if (resetSearch.value) {
        searchInputText.value = ''
        playerToPlayerUnlimitedStore.resetSearchTerm()
    }
})

watch(() => guessedPlayers.value.length, () => {
    console.log('myX:', myX.value)
    console.log('scrollRef:', scrollRef.value)
    console.log('arrivedState:', arrivedState.value)
    console.log('scrollY:', scrollY.value)
    scrollY.value += 100
}, { immediate: true })

</script>

<style lang="postcss" scoped>
.single-player-daily-container {
    @apply flex flex-row justify-center items-center h-screen;
    .won-container {
        @apply backdrop-blur-sm absolute z-30 flex flex-col justify-center items-center h-full w-full;
        .play-again {
            @apply w-fit p-2;
        }
    }
    .content-container {
        @apply flex flex-col flex-1 h-full py-40 bg-gray-100 items-center;
        .players-container {
            @apply flex flex-col flex-auto items-center py-5;
            /* https://stackoverflow.com/questions/18614301/keep-overflow-div-scrolled-to-bottom-unless-user-scrolls-up */
            /* https://codepen.io/anon/pen/pdrLEZ */
            .scrolling-players {
                @apply flex flex-col flex-auto items-center overflow-y-scroll overflow-x-hidden h-[200px];
                /* -ms-overflow-style: none;
                scrollbar-width: none;
                &::-webkit-scrollbar {
                    display: none;
                } */
            }
            .player {
                @apply flex-auto mt-3 pl-1 text-xl border-2 border-black w-[40%] min-w-[350px] max-w-xl bg-white;
                &.start {
                    @apply bg-green-500;
                }
                &.end {
                    @apply bg-red-500;
                }
            }
        }
        .search-block {
            @apply flex flex-col p-2 flex-1 items-center gap-4 bg-gray-100 w-[40%] min-w-[350px] max-w-xl;
            /* #search {
                @apply text-2xl;
            }
            .search-bar {
                @apply bg-gray-100 border border-black;
            } */
        }
    }
}
</style>
