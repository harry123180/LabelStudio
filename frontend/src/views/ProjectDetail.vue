<template>
  <div class="project-detail">
    <div class="header">
      <h1>{{ project?.name }}</h1>
      <p>{{ project?.description }}</p>
    </div>

    <div class="tabs">
      <button :class="{ active: activeTab === 'images' }" @click="activeTab = 'images'">
        📷 {{ $t('project.images') }}
      </button>
      <button :class="{ active: activeTab === 'classes' }" @click="activeTab = 'classes'">
        🏷️ {{ $t('project.classes') }}
      </button>
      <button :class="{ active: activeTab === 'split' }" @click="activeTab = 'split'">
        📊 {{ $t('project.split') }}
      </button>
      <button :class="{ active: activeTab === 'qrcode' }" @click="activeTab = 'qrcode'">
        📱 {{ $t('project.qrcode') }}
      </button>
      <button :class="{ active: activeTab === 'export' }" @click="activeTab = 'export'">
        📦 {{ $t('project.export') }}
      </button>
    </div>

    <div class="tab-content">
      <!-- Images Tab -->
      <div v-if="activeTab === 'images'" class="images-tab">
        <div class="upload-area">
          <input type="file" multiple accept="image/*" @change="handleUpload" />
          <p>{{ $t('upload.dragDrop') }}</p>
        </div>
        <div class="image-grid">
          <div v-for="image in images" :key="image.id" class="image-card">
            <img :src="`/api/images/${image.id}/file`" :alt="image.filename" />
            <div class="image-info">
              <span>{{ image.filename }}</span>
              <span class="badge" :class="image.status">{{ image.status }}</span>
            </div>
            <router-link :to="`/annotate/${project.id}/${image.id}`" class="annotate-btn">
              {{ $t('annotate.tools') }}
            </router-link>
          </div>
        </div>
      </div>

      <!-- QR Code Tab -->
      <div v-if="activeTab === 'qrcode'" class="qrcode-tab">
        <div class="qr-container">
          <img v-if="qrcode" :src="qrcode" alt="QR Code" class="qr-image" />
          <p class="qr-url">{{ qrUrl }}</p>
          <div class="qr-stats">
            <span>📷 {{ uploadStats.total_images }} images</span>
            <span>📱 {{ uploadStats.mobile_uploads }} from mobile</span>
          </div>
          <button class="btn btn-primary" @click="generateQR">
            {{ $t('common.refresh') || 'Refresh' }}
          </button>
        </div>
      </div>

      <!-- Other tabs placeholder -->
      <div v-if="activeTab === 'classes'" class="classes-tab">
        <p>Classes management coming soon...</p>
      </div>

      <div v-if="activeTab === 'split'" class="split-tab">
        <p>Dataset split coming soon...</p>
      </div>

      <div v-if="activeTab === 'export'" class="export-tab">
        <p>Export coming soon...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const projectId = route.params.id

const project = ref(null)
const images = ref([])
const activeTab = ref('images')
const qrcode = ref('')
const qrUrl = ref('')
const uploadStats = ref({ total_images: 0, mobile_uploads: 0 })

onMounted(async () => {
  await fetchProject()
  await fetchImages()
})

async function fetchProject() {
  const response = await axios.get(`/api/projects/${projectId}`)
  project.value = response.data
}

async function fetchImages() {
  const response = await axios.get(`/api/images/project/${projectId}`)
  images.value = response.data
}

async function handleUpload(event) {
  const files = event.target.files
  const formData = new FormData()
  for (const file of files) {
    formData.append('images', file)
  }

  await axios.post(`/api/images/project/${projectId}/upload`, formData)
  await fetchImages()
}

async function generateQR() {
  const response = await axios.get(`/api/qr/project/${projectId}`)
  qrcode.value = response.data.qrcode
  qrUrl.value = response.data.url

  const statsResponse = await axios.get(`/api/qr/project/${projectId}/stats`)
  uploadStats.value = statsResponse.data
}
</script>

<style scoped>
.project-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.header {
  margin-bottom: 2rem;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 1.5rem;
}

.tabs button {
  padding: 0.75rem 1rem;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.875rem;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
}

.tabs button.active {
  border-bottom-color: #4CAF50;
  color: #4CAF50;
}

.upload-area {
  border: 2px dashed #ccc;
  padding: 2rem;
  text-align: center;
  margin-bottom: 1.5rem;
  border-radius: 8px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.image-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-card img {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.image-info {
  padding: 0.5rem;
  font-size: 0.75rem;
  display: flex;
  justify-content: space-between;
}

.badge {
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 0.625rem;
}

.badge.pending { background: #ffc107; }
.badge.annotated { background: #4CAF50; color: white; }
.badge.reviewed { background: #2196F3; color: white; }

.annotate-btn {
  display: block;
  text-align: center;
  padding: 0.5rem;
  background: #4CAF50;
  color: white;
  text-decoration: none;
  font-size: 0.875rem;
}

.qrcode-tab {
  text-align: center;
}

.qr-container {
  display: inline-block;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.qr-image {
  width: 256px;
  height: 256px;
}

.qr-url {
  margin: 1rem 0;
  font-family: monospace;
  color: #666;
}

.qr-stats {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1rem;
}

.btn-primary {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}
</style>
