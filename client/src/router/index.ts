import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/singleplayer',
      name: 'singleplayer',
      component: () => import('../views/SinglePlayerView.vue'),
    },
    {
      path: '/multiplayer',
      name: 'multiplayer',
      component: () => import('../views/MultiPlayerHomeView.vue'),
    },
    {
      path: '/multiplayer/:code',
      name: 'multiplayer-lobby',
      component: () => import('../views/MultiPlayerLobbyView.vue'),
    },
  ],
})

export default router
