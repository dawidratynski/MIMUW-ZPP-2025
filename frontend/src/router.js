import { createWebHistory, createRouter } from 'vue-router'

import MapView from './views/MapView.vue'
import AboutView from './views/AboutView.vue'
import ForumView from './views/ForumView.vue'
import NotFound from './views/NotFound.vue'

const routes = [
  { path: '/', component: MapView },
  { path: '/about', component: AboutView },
  { path: '/forum/:itemId', component: ForumView, props: true },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
