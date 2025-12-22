/**
 * Project Store (Pinia)
 */
import { defineStore } from 'pinia'
import axios from 'axios'

export const useProjectStore = defineStore('project', {
  state: () => ({
    projects: [],
    currentProject: null,
    loading: false,
    error: null
  }),

  actions: {
    async fetchProjects() {
      this.loading = true
      try {
        const response = await axios.get('/api/projects')
        this.projects = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async fetchProject(id) {
      this.loading = true
      try {
        const response = await axios.get(`/api/projects/${id}`)
        this.currentProject = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async createProject(data) {
      const response = await axios.post('/api/projects', data)
      this.projects.push(response.data)
      return response.data
    },

    async deleteProject(id) {
      await axios.delete(`/api/projects/${id}`)
      this.projects = this.projects.filter(p => p.id !== id)
    }
  }
})
