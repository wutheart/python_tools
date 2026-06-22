import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: () => import('../views/JobListPage.vue') },
    { path: '/job/:id', name: 'job-detail', component: () => import('../views/JobDetailPage.vue') },
  ],
})

export default router
