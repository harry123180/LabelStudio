<template>
  <div class="projects">
    <div class="header">
      <h1>{{ $t('projects.title') }}</h1>
      <button class="btn btn-primary" @click="showCreateModal = true">
        + {{ $t('projects.create') }}
      </button>
    </div>

    <div v-if="loading" class="loading">
      {{ $t('common.loading') }}
    </div>

    <div v-else-if="projects.length === 0" class="empty">
      <p>No projects yet. Create your first project!</p>
    </div>

    <div v-else class="project-grid">
      <div v-for="project in projects" :key="project.id" class="project-card">
        <h3>{{ project.name }}</h3>
        <p class="description">{{ project.description || '-' }}</p>
        <div class="stats">
          <span>📷 {{ project.image_count }} {{ $t('projects.images') }}</span>
          <span>🏷️ {{ project.class_count }} {{ $t('project.classes') }}</span>
        </div>
        <div class="actions">
          <router-link :to="`/project/${project.id}`" class="btn btn-sm">
            {{ $t('projects.open') }}
          </router-link>
          <button class="btn btn-sm btn-danger" @click="deleteProject(project.id)">
            {{ $t('projects.delete') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <h2>{{ $t('projects.create') }}</h2>
        <form @submit.prevent="createProject">
          <div class="form-group">
            <label>{{ $t('projects.name') }}</label>
            <input v-model="newProject.name" required />
          </div>
          <div class="form-group">
            <label>{{ $t('projects.description') }}</label>
            <textarea v-model="newProject.description"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" class="btn" @click="showCreateModal = false">
              {{ $t('common.cancel') }}
            </button>
            <button type="submit" class="btn btn-primary">
              {{ $t('common.save') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const projects = ref([])
const loading = ref(true)
const showCreateModal = ref(false)
const newProject = ref({ name: '', description: '' })

onMounted(async () => {
  await fetchProjects()
})

async function fetchProjects() {
  try {
    const response = await axios.get('/api/projects')
    projects.value = response.data
  } catch (error) {
    console.error('Failed to fetch projects:', error)
  } finally {
    loading.value = false
  }
}

async function createProject() {
  try {
    await axios.post('/api/projects', newProject.value)
    showCreateModal.value = false
    newProject.value = { name: '', description: '' }
    await fetchProjects()
  } catch (error) {
    console.error('Failed to create project:', error)
  }
}

async function deleteProject(id) {
  if (confirm('Are you sure you want to delete this project?')) {
    try {
      await axios.delete(`/api/projects/${id}`)
      await fetchProjects()
    } catch (error) {
      console.error('Failed to delete project:', error)
    }
  }
}
</script>

<style scoped>
.projects {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.project-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.project-card h3 {
  margin-bottom: 0.5rem;
}

.project-card .description {
  color: #666;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.project-card .stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: #888;
}

.project-card .actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  font-size: 0.875rem;
  background: #e0e0e0;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group textarea {
  min-height: 100px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.loading, .empty {
  text-align: center;
  padding: 3rem;
  color: #666;
}
</style>
