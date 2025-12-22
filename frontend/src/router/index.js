/**
 * Vue Router Configuration
 */
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('@/views/Projects.vue')
  },
  {
    path: '/project/:id',
    name: 'Project',
    component: () => import('@/views/ProjectDetail.vue')
  },
  {
    path: '/annotate/:projectId/:imageId',
    name: 'Annotate',
    component: () => import('@/views/Annotate.vue')
  },
  {
    path: '/upload/:projectId',
    name: 'MobileUpload',
    component: () => import('@/views/MobileUpload.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
