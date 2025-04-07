import { createWebHistory, createRouter } from 'vue-router'

import MapView from './views/MapView.vue'
import AboutView from './views/AboutView.vue'
import ForumView from './views/ForumView.vue'

const routes = [
  { path: '/', component: MapView },
  { path: '/about', component: AboutView },
  { path: '/forum/:itemId', component: ForumView, props: true },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
