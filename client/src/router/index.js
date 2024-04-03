import { createRouter, createWebHistory } from 'vue-router'
import HomeScreen from '../views/HomeScreen.vue'
import SinglePlayer from '@/views/SinglePlayer.vue'
import SinglePlayerDaily from '@/views/SinglePlayerDaily.vue'
import SinglePlayerUnlimited from '@/views/SinglePlayerUnlimited.vue'
import BlockGame from '@/views/BlockGame.vue'

const routes = [
    {
        path: '/',
        name: 'home',
        component: HomeScreen
    },
    {
        path: '/single-player',
        name: 'single-player',
        component: SinglePlayer
    },
    {
        path: '/single-player/daily',
        name: 'single-player-daily',
        component: SinglePlayerDaily
    },
    {
        path: '/single-player/unlimited',
        name: 'single-player-unlimited',
        component: SinglePlayerUnlimited
    },
    {
        path: '/block-game',
        name: 'block-game',
        component: BlockGame
    }
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

export default router
