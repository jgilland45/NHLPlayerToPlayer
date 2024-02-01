import { createRouter, createWebHistory } from 'vue-router'
import HomeScreen from '../views/HomeScreen.vue'
import SinglePlayer from '@/views/SinglePlayer.vue'
import SinglePlayerDaily from '@/views/SinglePlayerDaily.vue'

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
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
