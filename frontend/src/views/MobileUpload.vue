<template>
  <div class="mobile-upload">
    <h2>{{ projectName }}</h2>

    <!-- Upload Area -->
    <div class="upload-area" @click="triggerInput">
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        multiple
        capture="environment"
        @change="handleFiles"
      />
      <div class="placeholder">
        <span class="icon">📷</span>
        <p>{{ $t('mobile.takePhoto') }}</p>
      </div>
    </div>

    <!-- Preview Grid -->
    <div v-if="selectedImages.length > 0" class="preview-grid">
      <div v-for="(img, idx) in selectedImages" :key="idx" class="preview-item">
        <img :src="img.preview" />
        <button class="remove-btn" @click="removeImage(idx)">✕</button>
      </div>
    </div>

    <!-- Nickname Input -->
    <input
      v-model="nickname"
      :placeholder="$t('mobile.nickname')"
      class="nickname-input"
    />

    <!-- Upload Button -->
    <button
      class="upload-btn"
      :disabled="selectedImages.length === 0 || uploading"
      @click="upload"
    >
      {{ uploading ? `${$t('upload.uploading')} ${progress}%` : `${$t('mobile.upload')} (${selectedImages.length})` }}
    </button>

    <!-- Success Message -->
    <div v-if="uploadSuccess" class="success-message">
      ✅ {{ $t('upload.success') }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const projectId = route.params.projectId

const projectName = ref('')
const selectedImages = ref([])
const nickname = ref('')
const uploading = ref(false)
const progress = ref(0)
const uploadSuccess = ref(false)
const fileInput = ref(null)

onMounted(async () => {
  try {
    const response = await axios.get(`/api/projects/${projectId}`)
    projectName.value = response.data.name
  } catch (error) {
    projectName.value = 'Upload'
  }
})

function triggerInput() {
  fileInput.value.click()
}

async function handleFiles(e) {
  const files = Array.from(e.target.files)

  for (const file of files) {
    const compressed = await compressImage(file, 1920, 0.8)
    selectedImages.value.push({
      file: compressed,
      preview: URL.createObjectURL(compressed)
    })
  }
}

function removeImage(idx) {
  URL.revokeObjectURL(selectedImages.value[idx].preview)
  selectedImages.value.splice(idx, 1)
}

async function compressImage(file, maxSize = 1920, quality = 0.8) {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        let { width, height } = img

        if (width > maxSize || height > maxSize) {
          if (width > height) {
            height = (height / width) * maxSize
            width = maxSize
          } else {
            width = (width / height) * maxSize
            height = maxSize
          }
        }

        canvas.width = width
        canvas.height = height

        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)

        canvas.toBlob(resolve, 'image/jpeg', quality)
      }
      img.src = e.target.result
    }
    reader.readAsDataURL(file)
  })
}

async function upload() {
  uploading.value = true
  progress.value = 0
  uploadSuccess.value = false

  const formData = new FormData()
  formData.append('nickname', nickname.value || '匿名')

  selectedImages.value.forEach(img => {
    formData.append('images', img.file, 'image.jpg')
  })

  try {
    const xhr = new XMLHttpRequest()

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        progress.value = Math.round((e.loaded / e.total) * 100)
      }
    }

    xhr.onload = () => {
      uploading.value = false
      if (xhr.status === 200) {
        uploadSuccess.value = true
        selectedImages.value.forEach(img => URL.revokeObjectURL(img.preview))
        selectedImages.value = []
      }
    }

    xhr.onerror = () => {
      uploading.value = false
      alert('Upload failed')
    }

    xhr.open('POST', `/api/qr/project/${projectId}/quick-upload`)
    xhr.send(formData)
  } catch (error) {
    uploading.value = false
    alert('Upload failed: ' + error.message)
  }
}
</script>

<style scoped>
.mobile-upload {
  max-width: 500px;
  margin: 0 auto;
  padding: 1rem;
  text-align: center;
}

h2 {
  margin-bottom: 1.5rem;
}

.upload-area {
  border: 2px dashed #ccc;
  border-radius: 12px;
  padding: 3rem 1rem;
  margin-bottom: 1rem;
  cursor: pointer;
}

.upload-area input[type="file"] {
  display: none;
}

.placeholder .icon {
  font-size: 4rem;
  display: block;
  margin-bottom: 0.5rem;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.preview-item {
  position: relative;
  aspect-ratio: 1;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  cursor: pointer;
  font-size: 12px;
}

.nickname-input {
  width: 100%;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  margin-bottom: 1rem;
}

.upload-btn {
  width: 100%;
  padding: 1rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.125rem;
  cursor: pointer;
}

.upload-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.success-message {
  margin-top: 1rem;
  padding: 1rem;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 8px;
}
</style>
