<template>
  <!-- Username Modal -->
  <div v-if="showUsernameModal" class="modal-overlay">
    <div class="modal username-modal">
      <h3>歡迎加入專案</h3>
      <p>請輸入你的名稱以開始標註工作</p>
      <form @submit.prevent="joinProject">
        <div class="form-group">
          <label>你的名稱</label>
          <input
            v-model="usernameInput"
            required
            placeholder="例如：小明"
            autofocus
          />
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="!usernameInput.trim()">
            加入專案
          </button>
        </div>
      </form>
    </div>
  </div>

  <div class="project-detail">
    <div class="header">
      <div class="header-main">
        <h1>{{ project?.name }}</h1>
        <p>{{ project?.description }}</p>
      </div>
      <div v-if="currentUsername" class="user-badge">
        <span class="user-icon">👤</span>
        <span>{{ currentUsername }}</span>
      </div>
    </div>

    <div class="tabs">
      <button :class="{ active: activeTab === 'tasks' }" @click="activeTab = 'tasks'; fetchMembers(); fetchImages()">
        開始標註
      </button>
      <button :class="{ active: activeTab === 'images' }" @click="activeTab = 'images'">
        {{ $t('project.images') }}
      </button>
      <button :class="{ active: activeTab === 'classes' }" @click="activeTab = 'classes'; fetchClasses()">
        {{ $t('project.classes') }}
      </button>
      <button :class="{ active: activeTab === 'split' }" @click="activeTab = 'split'">
        {{ $t('project.split') }}
      </button>
      <button :class="{ active: activeTab === 'qrcode' }" @click="activeTab = 'qrcode'; generateQR()">
        {{ $t('project.qrcode') }}
      </button>
      <button :class="{ active: activeTab === 'export' }" @click="activeTab = 'export'">
        {{ $t('project.export') }}
      </button>
    </div>

    <div class="tab-content">
      <!-- Images Tab -->
      <div v-if="activeTab === 'images'" class="images-tab">
        <div
          class="upload-area"
          :class="{ 'drag-over': isDragOver }"
          @dragover.prevent="isDragOver = true"
          @dragleave.prevent="isDragOver = false"
          @drop.prevent="handleDrop"
        >
          <input ref="fileInput" type="file" multiple accept="image/*" @change="handleUpload" />
          <input ref="folderInput" type="file" webkitdirectory multiple @change="handleUpload" />
          <div v-if="uploading" class="upload-progress">
            <span class="icon">⏳</span>
            <p>上傳中... {{ uploadProgress }}</p>
          </div>
          <div v-else class="upload-placeholder">
            <span class="icon">📁</span>
            <p>拖曳圖片或資料夾至此</p>
            <div class="upload-buttons">
              <button type="button" class="btn" @click="$refs.fileInput.click()">選擇圖片</button>
              <button type="button" class="btn" @click="$refs.folderInput.click()">選擇資料夾</button>
            </div>
          </div>
        </div>
        <div v-if="images.length === 0" class="empty-state">
          <p>{{ $t('project.noImages') || 'No images yet. Upload some images to get started.' }}</p>
        </div>
        <div v-else class="image-grid">
          <div v-for="image in images" :key="image.id" class="image-card">
            <img :src="`/api/images/${image.id}/file`" :alt="image.filename" />
            <div class="image-info">
              <span class="filename">{{ image.original_filename || image.filename }}</span>
              <span class="badge" :class="image.status || 'pending'">{{ image.status || 'pending' }}</span>
            </div>
            <div v-if="image.assigned_to" class="assigned-info">
              <span class="assigned-label">分配給:</span>
              <span class="assigned-user">{{ image.assigned_to }}</span>
            </div>
            <router-link :to="`/annotate/${project.id}/${image.id}`" class="annotate-btn">
              {{ $t('annotate.start') || 'Annotate' }}
            </router-link>
          </div>
        </div>
      </div>

      <!-- Tasks Tab -->
      <div v-if="activeTab === 'tasks'" class="tasks-tab">
        <!-- Progress Overview -->
        <div class="progress-overview">
          <div class="progress-bar-container">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
            </div>
            <span class="progress-text">{{ completedCount }} / {{ images.length }} 已完成 ({{ progressPercent }}%)</span>
          </div>
          <button class="btn btn-primary" @click="autoAssignImages" :disabled="members.length === 0 || unassignedCount === 0">
            自動分配未指派圖片
          </button>
        </div>

        <!-- My Tasks Section -->
        <div class="task-section">
          <h3>我的任務</h3>
          <div v-if="myTasks.length === 0" class="empty-hint">
            尚未分配任務給你，請等待或點擊上方自動分配
          </div>
          <div v-else class="task-grid">
            <div v-for="image in myTasks" :key="image.id" class="task-card" :class="{ completed: image.status === 'annotated' }">
              <img :src="`/api/images/${image.id}/file`" :alt="image.filename" />
              <div class="task-overlay">
                <span v-if="image.status === 'annotated'" class="status-badge done">已完成</span>
                <span v-else class="status-badge pending">待標註</span>
              </div>
              <router-link :to="`/annotate/${project.id}/${image.id}`" class="task-action">
                {{ image.status === 'annotated' ? '查看/編輯' : '開始標註' }}
              </router-link>
            </div>
          </div>
        </div>

        <!-- Team Progress Section -->
        <div class="task-section">
          <h3>團隊進度</h3>
          <div class="team-progress">
            <div v-for="member in members" :key="member.id" class="team-member">
              <div class="member-avatar-small">{{ member.display_name.charAt(0).toUpperCase() }}</div>
              <div class="member-progress-info">
                <div class="member-name-row">
                  <span class="name">{{ member.display_name }}</span>
                  <span class="progress-count">{{ member.images_completed || 0 }} / {{ member.images_assigned || 0 }}</span>
                </div>
                <div class="mini-progress-bar">
                  <div class="mini-progress-fill" :style="{ width: getMemberProgress(member) + '%' }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Help Others Section -->
        <div class="task-section">
          <h3>幫助隊友（未完成的任務）</h3>
          <div v-if="othersPendingTasks.length === 0" class="empty-hint">
            太棒了！所有任務都已完成
          </div>
          <div v-else class="task-grid">
            <div v-for="image in othersPendingTasks" :key="image.id" class="task-card help-card">
              <img :src="`/api/images/${image.id}/file`" :alt="image.filename" />
              <div class="task-overlay">
                <span class="assigned-to-badge">{{ image.assigned_to }}</span>
              </div>
              <router-link :to="`/annotate/${project.id}/${image.id}`" class="task-action help">
                幫忙標註
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Classes Tab -->
      <div v-if="activeTab === 'classes'" class="classes-tab">
        <div class="classes-header">
          <h2>{{ $t('project.labelClasses') || 'Label Classes' }}</h2>
          <button class="btn btn-primary" @click="showClassModal = true">
            + {{ $t('project.addClass') || 'Add Class' }}
          </button>
        </div>

        <div v-if="classes.length === 0" class="empty-state">
          <p>{{ $t('project.noClasses') || 'No classes defined. Add classes to start labeling.' }}</p>
        </div>

        <div v-else class="classes-list">
          <div v-for="cls in classes" :key="cls.id" class="class-item">
            <div class="class-color" :style="{ background: cls.color }"></div>
            <div class="class-info">
              <span class="class-name">{{ cls.name }}</span>
              <span v-if="cls.shortcut_key" class="shortcut">{{ cls.shortcut_key }}</span>
            </div>
            <div class="class-actions">
              <button class="btn-icon" @click="editClass(cls)" title="Edit">✏️</button>
              <button class="btn-icon" @click="deleteClass(cls.id)" title="Delete">🗑️</button>
            </div>
          </div>
        </div>

        <!-- Class Modal -->
        <div v-if="showClassModal" class="modal-overlay" @click.self="closeClassModal">
          <div class="modal">
            <h3>{{ editingClass ? 'Edit Class' : 'New Class' }}</h3>
            <form @submit.prevent="saveClass">
              <div class="form-group">
                <label>{{ $t('project.className') || 'Class Name' }}</label>
                <input v-model="classForm.name" required placeholder="e.g. Person, Car, Dog" />
              </div>
              <div class="form-group">
                <label>{{ $t('project.classColor') || 'Color' }}</label>
                <div class="color-picker">
                  <input type="color" v-model="classForm.color" />
                  <span>{{ classForm.color }}</span>
                </div>
              </div>
              <div class="form-group">
                <label>{{ $t('project.shortcutKey') || 'Shortcut Key' }}</label>
                <input v-model="classForm.shortcut_key" maxlength="1" placeholder="1-9" />
              </div>
              <div class="form-actions">
                <button type="button" class="btn" @click="closeClassModal">{{ $t('common.cancel') }}</button>
                <button type="submit" class="btn btn-primary">{{ $t('common.save') }}</button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Split Tab -->
      <div v-if="activeTab === 'split'" class="split-tab">
        <div class="split-header">
          <h2>{{ $t('project.datasetSplit') || 'Dataset Split' }}</h2>
        </div>

        <div class="split-controls">
          <div class="split-slider">
            <label>
              <span class="split-label train">Train</span>
              <span class="split-value">{{ splitRatios.train }}%</span>
            </label>
            <input type="range" v-model.number="splitRatios.train" min="0" max="100" @input="adjustSplit('train')" />
          </div>
          <div class="split-slider">
            <label>
              <span class="split-label val">Validation</span>
              <span class="split-value">{{ splitRatios.val }}%</span>
            </label>
            <input type="range" v-model.number="splitRatios.val" min="0" max="100" @input="adjustSplit('val')" />
          </div>
          <div class="split-slider">
            <label>
              <span class="split-label test">Test</span>
              <span class="split-value">{{ splitRatios.test }}%</span>
            </label>
            <input type="range" v-model.number="splitRatios.test" min="0" max="100" @input="adjustSplit('test')" />
          </div>
        </div>

        <div class="split-summary">
          <div class="split-bar">
            <div class="train-bar" :style="{ width: splitRatios.train + '%' }">
              {{ splitRatios.train }}%
            </div>
            <div class="val-bar" :style="{ width: splitRatios.val + '%' }">
              {{ splitRatios.val }}%
            </div>
            <div class="test-bar" :style="{ width: splitRatios.test + '%' }">
              {{ splitRatios.test }}%
            </div>
          </div>
          <div class="split-counts">
            <span class="train">Train: {{ Math.round(images.length * splitRatios.train / 100) }}</span>
            <span class="val">Val: {{ Math.round(images.length * splitRatios.val / 100) }}</span>
            <span class="test">Test: {{ Math.round(images.length * splitRatios.test / 100) }}</span>
            <span class="total">Total: {{ images.length }}</span>
          </div>
        </div>

        <div class="split-actions">
          <button class="btn btn-primary" @click="applySplit">
            套用分割
          </button>
          <button class="btn" @click="resetSplit">
            重置
          </button>
        </div>

        <!-- Data Augmentation Settings -->
        <div class="augmentation-section">
          <h3>數據增強設定</h3>
          <p class="aug-description">匯出時會對訓練集圖片套用這些增強，增加資料多樣性</p>

          <div class="aug-options">
            <label class="aug-option">
              <input type="checkbox" v-model="augmentation.enabled" />
              <span class="aug-name">啟用數據增強</span>
            </label>

            <div v-if="augmentation.enabled" class="aug-details">
              <label class="aug-option">
                <input type="checkbox" v-model="augmentation.flipHorizontal" />
                <span class="aug-name">水平翻轉</span>
                <span class="aug-desc">左右鏡像翻轉</span>
              </label>

              <label class="aug-option">
                <input type="checkbox" v-model="augmentation.flipVertical" />
                <span class="aug-name">垂直翻轉</span>
                <span class="aug-desc">上下翻轉</span>
              </label>

              <label class="aug-option">
                <input type="checkbox" v-model="augmentation.rotate90" />
                <span class="aug-name">旋轉 90°</span>
                <span class="aug-desc">順時針旋轉 90 度</span>
              </label>

              <label class="aug-option">
                <input type="checkbox" v-model="augmentation.brightness" />
                <span class="aug-name">亮度調整</span>
                <span class="aug-desc">隨機調整亮度 ±20%</span>
              </label>

              <label class="aug-option">
                <input type="checkbox" v-model="augmentation.contrast" />
                <span class="aug-name">對比度調整</span>
                <span class="aug-desc">隨機調整對比度</span>
              </label>

              <label class="aug-option">
                <input type="checkbox" v-model="augmentation.blur" />
                <span class="aug-name">模糊</span>
                <span class="aug-desc">輕微高斯模糊</span>
              </label>

              <label class="aug-option">
                <input type="checkbox" v-model="augmentation.noise" />
                <span class="aug-name">雜訊</span>
                <span class="aug-desc">添加隨機雜訊</span>
              </label>

              <div class="aug-multiplier">
                <label>增強倍數</label>
                <select v-model.number="augmentation.multiplier">
                  <option :value="1">1x (原圖 + 增強各 1 張)</option>
                  <option :value="2">2x (原圖 + 增強各 2 張)</option>
                  <option :value="3">3x (原圖 + 增強各 3 張)</option>
                  <option :value="5">5x (原圖 + 增強各 5 張)</option>
                </select>
                <p class="aug-estimate">
                  預估訓練集數量: {{ Math.round(images.length * splitRatios.train / 100) }} →
                  {{ estimatedAugmentedCount }} 張
                </p>
              </div>
            </div>
          </div>

          <button class="btn" @click="saveAugmentationSettings">
            儲存增強設定
          </button>
        </div>
      </div>

      <!-- QR Code Tab -->
      <div v-if="activeTab === 'qrcode'" class="qrcode-tab">
        <div class="qr-container">
          <div v-if="!qrcode" class="qr-loading">
            {{ $t('common.loading') || 'Loading...' }}
          </div>
          <template v-else>
            <img :src="qrcode" alt="QR Code" class="qr-image" />
            <p class="qr-url">{{ qrUrl }}</p>
            <div class="qr-stats">
              <span>{{ uploadStats.total_images }} {{ $t('project.images') }}</span>
              <span>{{ uploadStats.mobile_uploads }} {{ $t('project.fromMobile') || 'from mobile' }}</span>
            </div>
            <button class="btn btn-primary" @click="generateQR">
              {{ $t('common.refresh') || 'Refresh' }}
            </button>
          </template>
        </div>
      </div>

      <!-- Export Tab -->
      <div v-if="activeTab === 'export'" class="export-tab">
        <div class="export-header">
          <h2>{{ $t('project.exportData') || 'Export Data' }}</h2>
        </div>

        <div class="export-formats">
          <div
            v-for="format in exportFormats"
            :key="format.id"
            class="format-card"
            :class="{ selected: selectedFormat === format.id }"
            @click="selectedFormat = format.id"
          >
            <span class="format-icon">{{ format.icon }}</span>
            <span class="format-name">{{ format.name }}</span>
            <span class="format-desc">{{ format.description }}</span>
          </div>
        </div>

        <button class="btn btn-primary btn-large" @click="exportData" :disabled="exporting">
          {{ exporting ? ($t('project.exporting') || 'Exporting...') : ($t('project.export') || 'Export') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const projectId = route.params.id

const project = ref(null)
const images = ref([])
const classes = ref([])
const activeTab = ref('tasks')

// User/Member state
const showUsernameModal = ref(false)
const usernameInput = ref('')
const currentUsername = ref('')
const members = ref([])

// Computed stats for assignment
const unassignedCount = computed(() => images.value.filter(img => !img.assigned_to).length)
const assignedCount = computed(() => images.value.filter(img => img.assigned_to && img.status !== 'annotated').length)
const completedCount = computed(() => images.value.filter(img => img.status === 'annotated').length)
const progressPercent = computed(() => {
  if (images.value.length === 0) return 0
  return Math.round((completedCount.value / images.value.length) * 100)
})

// My tasks (images assigned to me)
const myTasks = computed(() => {
  return images.value.filter(img => img.assigned_to === currentUsername.value)
})

// Other members' pending tasks (not assigned to me, not completed)
const othersPendingTasks = computed(() => {
  return images.value.filter(img =>
    img.assigned_to &&
    img.assigned_to !== currentUsername.value &&
    img.status !== 'annotated'
  )
})

// Get member progress percentage
function getMemberProgress(member) {
  if (!member.images_assigned || member.images_assigned === 0) return 0
  return Math.round(((member.images_completed || 0) / member.images_assigned) * 100)
}

// Upload state
const uploading = ref(false)
const uploadProgress = ref('')
const isDragOver = ref(false)

// QR Code
const qrcode = ref('')
const qrUrl = ref('')
const uploadStats = ref({ total_images: 0, mobile_uploads: 0 })

// Classes
const showClassModal = ref(false)
const editingClass = ref(null)
const classForm = ref({ name: '', color: '#FF6B6B', shortcut_key: '' })

// Split
const splitRatios = ref({ train: 70, val: 20, test: 10 })

// Augmentation
const augmentation = ref({
  enabled: false,
  flipHorizontal: true,
  flipVertical: false,
  rotate90: false,
  brightness: true,
  contrast: false,
  blur: false,
  noise: false,
  multiplier: 1
})

// Computed: estimated augmented count
const estimatedAugmentedCount = computed(() => {
  if (!augmentation.value.enabled) {
    return Math.round(images.value.length * splitRatios.value.train / 100)
  }
  const trainCount = Math.round(images.value.length * splitRatios.value.train / 100)
  const enabledAugs = [
    augmentation.value.flipHorizontal,
    augmentation.value.flipVertical,
    augmentation.value.rotate90,
    augmentation.value.brightness,
    augmentation.value.contrast,
    augmentation.value.blur,
    augmentation.value.noise
  ].filter(Boolean).length
  // Original + (augmented versions per enabled augmentation * multiplier)
  return trainCount + (trainCount * enabledAugs * augmentation.value.multiplier)
})

// Export
const selectedFormat = ref('yolo')
const exporting = ref(false)
const exportFormats = [
  { id: 'yolo', name: 'YOLO', icon: '🎯', description: 'YOLOv5/v8 format' },
  { id: 'coco', name: 'COCO', icon: '📦', description: 'COCO JSON format' },
  { id: 'voc', name: 'Pascal VOC', icon: '📄', description: 'XML annotations' },
  { id: 'csv', name: 'CSV', icon: '📊', description: 'Simple CSV format' }
]

onMounted(async () => {
  await fetchProject()
  await fetchImages()
  await fetchMembers()
  loadAugmentationSettings()
  checkUsername()
})

function checkUsername() {
  // Check if user already has a username for this project
  const storedUsername = localStorage.getItem(`project_${projectId}_username`)
  if (storedUsername) {
    currentUsername.value = storedUsername
  } else {
    // Show modal to enter username
    showUsernameModal.value = true
  }
}

async function joinProject() {
  if (!usernameInput.value.trim()) return

  try {
    const response = await axios.post(`/api/members/project/${projectId}/join`, {
      username: usernameInput.value.trim()
    })

    currentUsername.value = response.data.username
    localStorage.setItem(`project_${projectId}_username`, response.data.username)

    if (response.data.was_renamed) {
      alert(`名稱已被使用，您的名稱已改為: ${response.data.username}`)
    }

    showUsernameModal.value = false
    usernameInput.value = ''
  } catch (error) {
    alert('加入專案失敗: ' + error.message)
  }
}

async function fetchMembers() {
  try {
    const response = await axios.get(`/api/members/project/${projectId}/members`)
    members.value = response.data
  } catch (error) {
    console.error('Failed to fetch members:', error)
  }
}

async function autoAssignImages() {
  try {
    const response = await axios.post(`/api/members/project/${projectId}/assign`, {
      mode: 'auto'
    })
    alert(`已自動分配 ${response.data.assigned} 張圖片給 ${response.data.members_count} 位成員`)
    await fetchImages()
    await fetchMembers()
  } catch (error) {
    alert('分配失敗: ' + error.message)
  }
}

async function fetchProject() {
  const response = await axios.get(`/api/projects/${projectId}`)
  project.value = response.data
  if (project.value.split_ratios) {
    splitRatios.value = {
      train: Math.round(project.value.split_ratios.train * 100),
      val: Math.round(project.value.split_ratios.val * 100),
      test: Math.round(project.value.split_ratios.test * 100)
    }
  }
}

async function fetchImages() {
  const response = await axios.get(`/api/images/project/${projectId}`)
  images.value = response.data
}

async function fetchClasses() {
  const response = await axios.get(`/api/projects/${projectId}/classes`)
  classes.value = response.data
}

async function handleDrop(e) {
  isDragOver.value = false
  const items = e.dataTransfer.items
  const files = []

  // Process items to handle folders
  const processEntry = async (entry) => {
    if (entry.isFile) {
      return new Promise((resolve) => {
        entry.file((file) => {
          if (file.type.startsWith('image/')) {
            files.push(file)
          }
          resolve()
        })
      })
    } else if (entry.isDirectory) {
      const reader = entry.createReader()
      return new Promise((resolve) => {
        reader.readEntries(async (entries) => {
          for (const ent of entries) {
            await processEntry(ent)
          }
          resolve()
        })
      })
    }
  }

  // Process all dropped items
  const promises = []
  for (const item of items) {
    const entry = item.webkitGetAsEntry?.()
    if (entry) {
      promises.push(processEntry(entry))
    }
  }
  await Promise.all(promises)

  if (files.length > 0) {
    await uploadFiles(files)
  }
}

async function handleUpload(event) {
  const fileList = event.target.files
  // Filter image files only (for folder input which may include non-images)
  const files = Array.from(fileList).filter(f => f.type.startsWith('image/'))
  if (files.length > 0) {
    await uploadFiles(files)
  }
  // Reset input so same file can be selected again
  event.target.value = ''
}

async function uploadFiles(files) {
  uploading.value = true
  const totalFiles = files.length
  let uploadedCount = 0
  let failedCount = 0

  // Upload in batches of 5 files to avoid overwhelming the server
  const BATCH_SIZE = 5

  try {
    for (let i = 0; i < files.length; i += BATCH_SIZE) {
      const batch = files.slice(i, i + BATCH_SIZE)
      uploadProgress.value = `${uploadedCount} / ${totalFiles} 張圖片`

      const formData = new FormData()
      for (const file of batch) {
        formData.append('images', file)
      }

      try {
        await axios.post(`/api/images/project/${projectId}/upload`, formData)
        uploadedCount += batch.length
      } catch (err) {
        console.error('Batch upload failed:', err)
        failedCount += batch.length
      }
    }

    if (failedCount > 0) {
      uploadProgress.value = `完成！已上傳 ${uploadedCount} 張，失敗 ${failedCount} 張`
    } else {
      uploadProgress.value = `完成！已上傳 ${uploadedCount} 張圖片`
    }
    await fetchImages()
  } catch (error) {
    alert('上傳失敗: ' + error.message)
  } finally {
    setTimeout(() => {
      uploading.value = false
      uploadProgress.value = ''
    }, 2000)
  }
}

async function generateQR() {
  const response = await axios.get(`/api/qr/project/${projectId}`)
  qrcode.value = response.data.qrcode
  qrUrl.value = response.data.url

  const statsResponse = await axios.get(`/api/qr/project/${projectId}/stats`)
  uploadStats.value = statsResponse.data
}

// Class management
function editClass(cls) {
  editingClass.value = cls
  classForm.value = { ...cls }
  showClassModal.value = true
}

function closeClassModal() {
  showClassModal.value = false
  editingClass.value = null
  classForm.value = { name: '', color: '#FF6B6B', shortcut_key: '' }
}

async function saveClass() {
  if (editingClass.value) {
    await axios.put(`/api/projects/${projectId}/classes/${editingClass.value.id}`, classForm.value)
  } else {
    await axios.post(`/api/projects/${projectId}/classes`, classForm.value)
  }
  await fetchClasses()
  closeClassModal()
}

async function deleteClass(id) {
  if (confirm('Delete this class?')) {
    await axios.delete(`/api/projects/${projectId}/classes/${id}`)
    await fetchClasses()
  }
}

// Split management
function adjustSplit(changed) {
  const total = splitRatios.value.train + splitRatios.value.val + splitRatios.value.test
  if (total !== 100) {
    const diff = total - 100
    if (changed === 'train') {
      splitRatios.value.val = Math.max(0, splitRatios.value.val - Math.ceil(diff / 2))
      splitRatios.value.test = 100 - splitRatios.value.train - splitRatios.value.val
    } else if (changed === 'val') {
      splitRatios.value.test = Math.max(0, splitRatios.value.test - diff)
      if (splitRatios.value.test < 0) {
        splitRatios.value.train = Math.max(0, splitRatios.value.train + splitRatios.value.test)
        splitRatios.value.test = 0
      }
    } else {
      splitRatios.value.val = Math.max(0, splitRatios.value.val - diff)
      if (splitRatios.value.val < 0) {
        splitRatios.value.train = Math.max(0, splitRatios.value.train + splitRatios.value.val)
        splitRatios.value.val = 0
      }
    }
  }
}

async function applySplit() {
  await axios.put(`/api/projects/${projectId}`, {
    train_ratio: splitRatios.value.train / 100,
    val_ratio: splitRatios.value.val / 100,
    test_ratio: splitRatios.value.test / 100
  })
  // Apply to images
  await axios.post(`/api/projects/${projectId}/apply-split`)
  await fetchImages()
  alert('Split applied successfully!')
}

function resetSplit() {
  splitRatios.value = { train: 70, val: 20, test: 10 }
}

// Augmentation
function loadAugmentationSettings() {
  const saved = localStorage.getItem(`project_${projectId}_augmentation`)
  if (saved) {
    try {
      augmentation.value = JSON.parse(saved)
    } catch (e) {
      console.error('Failed to load augmentation settings:', e)
    }
  }
}

function saveAugmentationSettings() {
  localStorage.setItem(`project_${projectId}_augmentation`, JSON.stringify(augmentation.value))
  alert('增強設定已儲存！')
}

// Export
async function exportData() {
  exporting.value = true
  try {
    const response = await axios.post(`/api/projects/${projectId}/export`, {
      format: selectedFormat.value,
      includeImages: true,
      onlyAnnotated: true,
      augmentation: augmentation.value
    }, { responseType: 'blob' })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${project.value.name}_${selectedFormat.value}.zip`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    alert('Export failed: ' + error.message)
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.project-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.header-main h1 {
  margin-bottom: 0.5rem;
}

.header-main p {
  color: #666;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #4CAF50;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
}

.user-icon {
  font-size: 1rem;
}

/* Username Modal */
.username-modal {
  text-align: center;
}

.username-modal h3 {
  margin-bottom: 0.5rem;
}

.username-modal p {
  color: #666;
  margin-bottom: 1.5rem;
}

.username-modal input {
  text-align: center;
  font-size: 1.1rem;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 1.5rem;
  overflow-x: auto;
}

.tabs button {
  padding: 0.75rem 1rem;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.875rem;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  white-space: nowrap;
}

.tabs button.active {
  border-bottom-color: #4CAF50;
  color: #4CAF50;
}

/* Images Tab */
.upload-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: #4CAF50;
}

.upload-area.drag-over {
  border-color: #4CAF50;
  background: rgba(76, 175, 80, 0.1);
}

.upload-area input[type="file"] {
  display: none;
}

.upload-placeholder,
.upload-progress {
  padding: 2rem;
  text-align: center;
}

.upload-placeholder .icon,
.upload-progress .icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 0.5rem;
}

.upload-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1rem;
}

.upload-buttons .btn {
  padding: 0.5rem 1.5rem;
}

.upload-progress {
  color: #4CAF50;
}

.upload-progress p {
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #666;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-info .filename {
  font-size: 0.75rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 120px;
}

.badge {
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 0.625rem;
  text-transform: uppercase;
}

.badge.pending { background: #ffc107; }
.badge.annotated { background: #4CAF50; color: white; }
.badge.reviewed { background: #2196F3; color: white; }

.assigned-info {
  padding: 0.25rem 0.5rem;
  background: #f5f5f5;
  font-size: 0.75rem;
  color: #666;
}

.assigned-label {
  color: #999;
}

.assigned-user {
  font-weight: 500;
  color: #333;
}

.annotate-btn {
  display: block;
  text-align: center;
  padding: 0.5rem;
  background: #4CAF50;
  color: white;
  text-decoration: none;
  font-size: 0.875rem;
}

.annotate-btn:hover {
  background: #45a049;
}

/* Classes Tab */
.classes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.classes-header h2 {
  margin: 0;
}

.classes-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.class-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.class-color {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  flex-shrink: 0;
}

.class-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.class-name {
  font-weight: 500;
}

.shortcut {
  background: #eee;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-family: monospace;
}

.class-actions {
  display: flex;
  gap: 0.25rem;
}

.btn-icon {
  border: none;
  background: none;
  cursor: pointer;
  padding: 0.25rem;
  font-size: 1rem;
  opacity: 0.6;
}

.btn-icon:hover {
  opacity: 1;
}

/* Split Tab */
.split-header {
  margin-bottom: 2rem;
}

.split-controls {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.split-slider {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.split-slider label {
  display: flex;
  justify-content: space-between;
  font-weight: 500;
}

.split-label {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.split-label.train { background: #4CAF50; color: white; }
.split-label.val { background: #2196F3; color: white; }
.split-label.test { background: #FF9800; color: white; }

.split-slider input[type="range"] {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  appearance: none;
  background: #ddd;
}

.split-slider input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #4CAF50;
  cursor: pointer;
}

.split-summary {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.split-bar {
  display: flex;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.split-bar > div {
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
  font-size: 0.875rem;
  transition: width 0.3s;
}

.train-bar { background: #4CAF50; }
.val-bar { background: #2196F3; }
.test-bar { background: #FF9800; }

.split-counts {
  display: flex;
  justify-content: space-around;
  font-size: 0.875rem;
}

.split-counts .train { color: #4CAF50; }
.split-counts .val { color: #2196F3; }
.split-counts .test { color: #FF9800; }
.split-counts .total { font-weight: 500; }

.split-actions {
  display: flex;
  gap: 1rem;
}

/* Augmentation Section */
.augmentation-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.augmentation-section h3 {
  margin-bottom: 0.5rem;
  color: #333;
}

.aug-description {
  color: #666;
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

.aug-options {
  margin-bottom: 1rem;
}

.aug-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.2s;
}

.aug-option:hover {
  background: #f5f5f5;
}

.aug-option input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #4CAF50;
}

.aug-name {
  font-weight: 500;
  min-width: 100px;
}

.aug-desc {
  color: #888;
  font-size: 0.875rem;
}

.aug-details {
  margin-left: 1rem;
  padding-left: 1rem;
  border-left: 3px solid #4CAF50;
  margin-top: 0.5rem;
}

.aug-multiplier {
  margin-top: 1rem;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 6px;
}

.aug-multiplier label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.aug-multiplier select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.aug-estimate {
  margin-top: 0.75rem;
  font-size: 0.875rem;
  color: #4CAF50;
  font-weight: 500;
}

/* QR Code Tab */
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

.qr-loading {
  padding: 4rem;
  color: #666;
}

.qr-image {
  width: 256px;
  height: 256px;
}

.qr-url {
  margin: 1rem 0;
  font-family: monospace;
  color: #666;
  word-break: break-all;
}

.qr-stats {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: #666;
}

/* Export Tab */
.export-header {
  margin-bottom: 2rem;
}

.export-formats {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.format-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border: 2px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.format-card:hover {
  border-color: #4CAF50;
}

.format-card.selected {
  border-color: #4CAF50;
  background: #f0fff0;
}

.format-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.format-name {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.format-desc {
  font-size: 0.75rem;
  color: #666;
}

.export-options {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

/* Common */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  background: #e0e0e0;
}

.btn:hover {
  background: #d0d0d0;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background: #45a049;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-large {
  padding: 1rem 2rem;
  font-size: 1rem;
}

/* Modal */
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
  max-width: 400px;
}

.modal h3 {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.color-picker {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.color-picker input[type="color"] {
  width: 50px;
  height: 36px;
  padding: 0;
  border: none;
  cursor: pointer;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

/* Tasks Tab */
.tasks-tab {
  max-width: 1000px;
}

.progress-overview {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.progress-bar-container {
  flex: 1;
}

.progress-bar {
  height: 12px;
  background: #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #81C784);
  transition: width 0.3s;
}

.progress-text {
  font-size: 0.875rem;
  color: #666;
}

.task-section {
  margin-bottom: 2rem;
}

.task-section h3 {
  margin-bottom: 1rem;
  color: #333;
}

.empty-hint {
  color: #999;
  font-style: italic;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
  text-align: center;
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 1rem;
}

.task-card {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: white;
}

.task-card img {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.task-card.completed img {
  opacity: 0.7;
}

.task-overlay {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.done {
  background: #4CAF50;
  color: white;
}

.status-badge.pending {
  background: #FF9800;
  color: white;
}

.assigned-to-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  background: rgba(0, 0, 0, 0.6);
  color: white;
}

.task-action {
  display: block;
  text-align: center;
  padding: 0.5rem;
  background: #4CAF50;
  color: white;
  text-decoration: none;
  font-size: 0.875rem;
}

.task-action:hover {
  background: #45a049;
}

.task-action.help {
  background: #2196F3;
}

.task-action.help:hover {
  background: #1976D2;
}

.help-card {
  border: 2px dashed #2196F3;
}

.team-progress {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.team-member {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.member-avatar-small {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4CAF50, #81C784);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: bold;
}

.member-progress-info {
  flex: 1;
}

.member-name-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.member-name-row .name {
  font-weight: 500;
}

.member-name-row .progress-count {
  font-size: 0.875rem;
  color: #666;
}

.mini-progress-bar {
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

.mini-progress-fill {
  height: 100%;
  background: #4CAF50;
  transition: width 0.3s;
}

/* Members Tab (legacy, kept for compatibility) */
.members-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.members-header h2 {
  margin: 0;
}

.members-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.member-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.member-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4CAF50, #81C784);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: bold;
}

.member-info {
  flex: 1;
}

.member-name {
  font-weight: 600;
  font-size: 1rem;
}

.member-username {
  color: #666;
  font-size: 0.875rem;
}

.member-stats {
  display: flex;
  gap: 1rem;
}

.member-stats .stat {
  text-align: center;
}

.member-stats .stat-value {
  display: block;
  font-size: 1.25rem;
  font-weight: bold;
  color: #4CAF50;
}

.member-stats .stat-label {
  font-size: 0.75rem;
  color: #999;
}

.assignment-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.assignment-section h3 {
  margin-bottom: 1rem;
}

.assignment-stats {
  display: flex;
  gap: 1rem;
}

.stat-card {
  flex: 1;
  text-align: center;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
}

.stat-card .stat-number {
  display: block;
  font-size: 2rem;
  font-weight: bold;
  color: #333;
}

.stat-card .stat-desc {
  font-size: 0.875rem;
  color: #666;
}
</style>
