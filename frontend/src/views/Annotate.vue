<template>
  <div class="annotate">
    <div class="toolbar">
      <div class="tool-group">
        <button
          v-for="tool in tools"
          :key="tool.id"
          :class="{ active: activeTool === tool.id }"
          :title="`${tool.name} (${tool.key})`"
          @click="activeTool = tool.id"
        >
          {{ tool.icon }}
        </button>
      </div>
      <div class="tool-group">
        <button @click="undo" title="Undo (Ctrl+Z)" :disabled="historyIndex <= 0">↶</button>
        <button @click="redo" title="Redo (Ctrl+Y)" :disabled="historyIndex >= history.length - 1">↷</button>
      </div>
      <div class="tool-group">
        <button @click="save" class="save-btn" :disabled="saving">
          {{ saving ? '...' : '💾' }} {{ $t('annotate.save') || 'Save' }}
        </button>
      </div>
      <div class="nav-group">
        <button @click="prevImage" :disabled="currentIndex <= 0">◀ {{ $t('annotate.prev') || 'Prev' }}</button>
        <span class="nav-info">{{ currentIndex + 1 }} / {{ imageList.length }}</span>
        <button @click="nextImage" :disabled="currentIndex >= imageList.length - 1">{{ $t('annotate.next') || 'Next' }} ▶</button>
      </div>
    </div>

    <div class="workspace">
      <div class="canvas-container" ref="canvasContainer">
        <canvas
          ref="canvas"
          @mousedown="handleMouseDown"
          @mousemove="handleMouseMove"
          @mouseup="handleMouseUp"
          @wheel="handleWheel"
        ></canvas>
      </div>

      <div class="sidebar">
        <div class="classes-panel">
          <h3>{{ $t('annotate.classes') || 'Classes' }}</h3>
          <div v-if="classes.length === 0" class="empty-hint info">
            💡 尚未定義類別<br>
            直接在圖片上畫框即可建立
          </div>
          <div
            v-for="cls in classes"
            :key="cls.id"
            :class="{ active: activeClass === cls.id }"
            class="class-item"
            @click="selectClass(cls.id)"
          >
            <span class="color-dot" :style="{ background: cls.color }"></span>
            <span class="class-name">{{ cls.name }}</span>
            <span v-if="cls.shortcut_key" class="shortcut">{{ cls.shortcut_key }}</span>
          </div>
        </div>

        <div class="annotations-panel">
          <h3>{{ $t('annotate.annotations') || 'Annotations' }} ({{ annotations.length }})</h3>
          <div v-if="annotations.length === 0" class="empty-hint">
            Draw bounding boxes on the image
          </div>
          <div
            v-for="(anno, idx) in annotations"
            :key="anno.id || idx"
            class="annotation-item"
            :class="{ selected: selectedAnnotation === idx }"
            @click="selectAnnotation(idx)"
          >
            <span class="color-dot" :style="{ background: getClassColor(anno.label_class_id) }"></span>
            <span class="anno-label">{{ getClassName(anno.label_class_id) }}</span>
            <button class="delete-btn" @click.stop="deleteAnnotation(idx)">🗑</button>
          </div>
        </div>

        <div class="info-panel">
          <h3>Info</h3>
          <div class="info-item">
            <span>Image:</span>
            <span>{{ currentImage?.original_filename || currentImage?.filename }}</span>
          </div>
          <div class="info-item">
            <span>Size:</span>
            <span>{{ currentImage?.width }} x {{ currentImage?.height }}</span>
          </div>
          <div class="info-item">
            <span>Zoom:</span>
            <span>{{ Math.round(scale * 100) }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const projectId = route.params.projectId
const imageId = ref(route.params.imageId)

// Refs
const canvas = ref(null)
const canvasContainer = ref(null)
const ctx = ref(null)

// State
const currentImage = ref(null)
const imageElement = ref(null)
const classes = ref([])
const annotations = ref([])
const imageList = ref([])
const currentIndex = ref(0)

const activeTool = ref('bbox')
const activeClass = ref(null)
const selectedAnnotation = ref(null)
const saving = ref(false)

// Canvas state
const scale = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)
const isDrawing = ref(false)
const isPanning = ref(false)
const isMoving = ref(false)
const isResizing = ref(false)
const resizeEdge = ref(null) // 'n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw'
const startX = ref(0)
const startY = ref(0)
const currentRect = ref(null)
const dragStartAnno = ref(null) // Store original annotation data when dragging

// History for undo/redo
const history = ref([])
const historyIndex = ref(-1)

const tools = [
  { id: 'select', name: 'Select', icon: '👆', key: 'V' },
  { id: 'bbox', name: 'Bounding Box', icon: '⬜', key: 'B' },
  { id: 'pan', name: 'Pan', icon: '✋', key: 'H' },
  { id: 'zoom', name: 'Zoom', icon: '🔍', key: 'Z' }
]

// Initialize
onMounted(async () => {
  await fetchClasses()
  await fetchImageList()
  await loadImage()
  initCanvas()
  window.addEventListener('keydown', handleKeydown)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('resize', handleResize)
})

// Fetch data
async function fetchClasses() {
  const response = await axios.get(`/api/projects/${projectId}/classes`)
  classes.value = response.data
  if (classes.value.length > 0 && !activeClass.value) {
    activeClass.value = classes.value[0].id
  }
}

async function fetchImageList() {
  const response = await axios.get(`/api/images/project/${projectId}`)
  imageList.value = response.data
  currentIndex.value = imageList.value.findIndex(img => img.id == imageId.value)
  if (currentIndex.value === -1) currentIndex.value = 0
}

async function loadImage() {
  const response = await axios.get(`/api/images/${imageId.value}`)
  currentImage.value = response.data

  // Load annotations
  const annoResponse = await axios.get(`/api/annotations/image/${imageId.value}`)
  annotations.value = annoResponse.data

  // Save initial state
  saveHistory()

  // Load image element
  imageElement.value = new Image()
  imageElement.value.onload = () => {
    fitImageToCanvas()
    render()
  }
  imageElement.value.src = `/api/images/${imageId.value}/file`
}

function initCanvas() {
  if (!canvas.value) return
  ctx.value = canvas.value.getContext('2d')
  handleResize()
}

function handleResize() {
  if (!canvas.value || !canvasContainer.value) return
  canvas.value.width = canvasContainer.value.clientWidth
  canvas.value.height = canvasContainer.value.clientHeight
  if (imageElement.value?.complete) {
    fitImageToCanvas()
    render()
  }
}

function fitImageToCanvas() {
  if (!imageElement.value || !canvas.value) return

  const containerWidth = canvas.value.width
  const containerHeight = canvas.value.height
  const imgWidth = imageElement.value.width
  const imgHeight = imageElement.value.height

  const scaleX = containerWidth / imgWidth
  const scaleY = containerHeight / imgHeight
  scale.value = Math.min(scaleX, scaleY) * 0.9

  offsetX.value = (containerWidth - imgWidth * scale.value) / 2
  offsetY.value = (containerHeight - imgHeight * scale.value) / 2
}

// Rendering
function render() {
  if (!ctx.value || !canvas.value) return

  const c = ctx.value
  c.clearRect(0, 0, canvas.value.width, canvas.value.height)

  // Draw background
  c.fillStyle = '#1a1a1a'
  c.fillRect(0, 0, canvas.value.width, canvas.value.height)

  // Draw image
  if (imageElement.value?.complete) {
    c.save()
    c.translate(offsetX.value, offsetY.value)
    c.scale(scale.value, scale.value)
    c.drawImage(imageElement.value, 0, 0)

    // Draw annotations
    annotations.value.forEach((anno, idx) => {
      const cls = classes.value.find(c => c.id === anno.label_class_id)
      const color = cls?.color || '#FF0000'
      const isSelected = selectedAnnotation.value === idx

      c.strokeStyle = color
      c.lineWidth = isSelected ? 3 / scale.value : 2 / scale.value
      c.fillStyle = color + '33' // 20% opacity

      const { x, y, width, height } = anno.data
      c.fillRect(x, y, width, height)
      c.strokeRect(x, y, width, height)

      // Draw label
      c.fillStyle = color
      c.font = `${14 / scale.value}px sans-serif`
      c.fillText(cls?.name || 'Unknown', x, y - 4 / scale.value)

      // Draw resize handles for selected annotation
      if (isSelected) {
        const handleSize = 8 / scale.value
        c.fillStyle = '#FFFFFF'
        c.strokeStyle = color
        c.lineWidth = 1 / scale.value

        // Corner handles
        const handles = [
          { x: x - handleSize / 2, y: y - handleSize / 2 }, // NW
          { x: x + width - handleSize / 2, y: y - handleSize / 2 }, // NE
          { x: x - handleSize / 2, y: y + height - handleSize / 2 }, // SW
          { x: x + width - handleSize / 2, y: y + height - handleSize / 2 }, // SE
          // Edge midpoints
          { x: x + width / 2 - handleSize / 2, y: y - handleSize / 2 }, // N
          { x: x + width / 2 - handleSize / 2, y: y + height - handleSize / 2 }, // S
          { x: x - handleSize / 2, y: y + height / 2 - handleSize / 2 }, // W
          { x: x + width - handleSize / 2, y: y + height / 2 - handleSize / 2 }, // E
        ]

        handles.forEach(h => {
          c.fillRect(h.x, h.y, handleSize, handleSize)
          c.strokeRect(h.x, h.y, handleSize, handleSize)
        })
      }
    })

    // Draw current rect being drawn
    if (currentRect.value) {
      const cls = classes.value.find(c => c.id === activeClass.value)
      c.strokeStyle = cls?.color || '#FF0000'
      c.lineWidth = 2 / scale.value
      c.setLineDash([5 / scale.value, 5 / scale.value])
      c.strokeRect(
        currentRect.value.x,
        currentRect.value.y,
        currentRect.value.width,
        currentRect.value.height
      )
      c.setLineDash([])
    }

    c.restore()
  }
}

// Quick class creation
async function promptCreateClass() {
  const name = prompt('請輸入新類別名稱 / Enter new class name:')
  if (!name || !name.trim()) return null

  // Generate random color
  const hue = Math.floor(Math.random() * 360)
  const color = `hsl(${hue}, 70%, 50%)`

  // Find next available shortcut key
  const usedKeys = classes.value.map(c => c.shortcut_key).filter(Boolean)
  let shortcutKey = null
  for (let i = 1; i <= 9; i++) {
    if (!usedKeys.includes(String(i))) {
      shortcutKey = String(i)
      break
    }
  }

  try {
    const response = await axios.post(`/api/projects/${projectId}/classes`, {
      name: name.trim(),
      color: color,
      shortcut_key: shortcutKey
    })
    classes.value.push(response.data)
    activeClass.value = response.data.id
    return response.data
  } catch (error) {
    alert('建立類別失敗: ' + error.message)
    return null
  }
}

// Edge detection for resize
const EDGE_THRESHOLD = 8 // pixels

function getEdgeAtPoint(anno, imgX, imgY) {
  const d = anno.data
  const threshold = EDGE_THRESHOLD / scale.value

  const nearLeft = Math.abs(imgX - d.x) < threshold
  const nearRight = Math.abs(imgX - (d.x + d.width)) < threshold
  const nearTop = Math.abs(imgY - d.y) < threshold
  const nearBottom = Math.abs(imgY - (d.y + d.height)) < threshold
  const inHorizontal = imgX > d.x - threshold && imgX < d.x + d.width + threshold
  const inVertical = imgY > d.y - threshold && imgY < d.y + d.height + threshold

  if (nearTop && nearLeft) return 'nw'
  if (nearTop && nearRight) return 'ne'
  if (nearBottom && nearLeft) return 'sw'
  if (nearBottom && nearRight) return 'se'
  if (nearTop && inHorizontal) return 'n'
  if (nearBottom && inHorizontal) return 's'
  if (nearLeft && inVertical) return 'w'
  if (nearRight && inVertical) return 'e'

  // Check if inside for move
  if (imgX > d.x && imgX < d.x + d.width && imgY > d.y && imgY < d.y + d.height) {
    return 'move'
  }

  return null
}

function getCursorForEdge(edge) {
  const cursors = {
    'n': 'ns-resize',
    's': 'ns-resize',
    'e': 'ew-resize',
    'w': 'ew-resize',
    'ne': 'nesw-resize',
    'sw': 'nesw-resize',
    'nw': 'nwse-resize',
    'se': 'nwse-resize',
    'move': 'move'
  }
  return cursors[edge] || 'crosshair'
}

// Mouse handlers
async function handleMouseDown(e) {
  const rect = canvas.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const imgX = (x - offsetX.value) / scale.value
  const imgY = (y - offsetY.value) / scale.value

  if (activeTool.value === 'pan' || e.button === 1) {
    isPanning.value = true
    startX.value = x - offsetX.value
    startY.value = y - offsetY.value
    canvas.value.style.cursor = 'grabbing'
  } else if (activeTool.value === 'bbox') {
    // Check if clicking on existing annotation for move/resize
    if (selectedAnnotation.value !== null) {
      const anno = annotations.value[selectedAnnotation.value]
      const edge = getEdgeAtPoint(anno, imgX, imgY)

      if (edge === 'move') {
        isMoving.value = true
        startX.value = imgX
        startY.value = imgY
        dragStartAnno.value = JSON.parse(JSON.stringify(anno.data))
        canvas.value.style.cursor = 'move'
        return
      } else if (edge) {
        isResizing.value = true
        resizeEdge.value = edge
        startX.value = imgX
        startY.value = imgY
        dragStartAnno.value = JSON.parse(JSON.stringify(anno.data))
        canvas.value.style.cursor = getCursorForEdge(edge)
        return
      }
    }

    // Check if clicking on any annotation to select it
    for (let i = annotations.value.length - 1; i >= 0; i--) {
      const anno = annotations.value[i]
      const edge = getEdgeAtPoint(anno, imgX, imgY)
      if (edge) {
        selectedAnnotation.value = i
        if (edge === 'move') {
          isMoving.value = true
          startX.value = imgX
          startY.value = imgY
          dragStartAnno.value = JSON.parse(JSON.stringify(anno.data))
          canvas.value.style.cursor = 'move'
        } else {
          isResizing.value = true
          resizeEdge.value = edge
          startX.value = imgX
          startY.value = imgY
          dragStartAnno.value = JSON.parse(JSON.stringify(anno.data))
          canvas.value.style.cursor = getCursorForEdge(edge)
        }
        render()
        return
      }
    }

    // Start drawing new box - check if we have a class
    if (!activeClass.value) {
      const newClass = await promptCreateClass()
      if (!newClass) return
    }

    isDrawing.value = true
    startX.value = imgX
    startY.value = imgY
    currentRect.value = { x: imgX, y: imgY, width: 0, height: 0 }
  } else if (activeTool.value === 'select') {
    selectAnnotationAt(imgX, imgY)
  }
}

function handleMouseMove(e) {
  const rect = canvas.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const imgX = (x - offsetX.value) / scale.value
  const imgY = (y - offsetY.value) / scale.value

  if (isPanning.value) {
    offsetX.value = x - startX.value
    offsetY.value = y - startY.value
    render()
  } else if (isMoving.value && selectedAnnotation.value !== null) {
    // Move annotation
    const anno = annotations.value[selectedAnnotation.value]
    const dx = imgX - startX.value
    const dy = imgY - startY.value
    anno.data.x = dragStartAnno.value.x + dx
    anno.data.y = dragStartAnno.value.y + dy
    render()
  } else if (isResizing.value && selectedAnnotation.value !== null) {
    // Resize annotation
    const anno = annotations.value[selectedAnnotation.value]
    const d = dragStartAnno.value
    const edge = resizeEdge.value

    let newX = d.x
    let newY = d.y
    let newW = d.width
    let newH = d.height

    if (edge.includes('w')) {
      newX = imgX
      newW = d.x + d.width - imgX
    }
    if (edge.includes('e')) {
      newW = imgX - d.x
    }
    if (edge.includes('n')) {
      newY = imgY
      newH = d.y + d.height - imgY
    }
    if (edge.includes('s')) {
      newH = imgY - d.y
    }

    // Ensure minimum size and handle flipping
    if (newW < 0) {
      newX = newX + newW
      newW = -newW
    }
    if (newH < 0) {
      newY = newY + newH
      newH = -newH
    }

    anno.data.x = newX
    anno.data.y = newY
    anno.data.width = Math.max(5, newW)
    anno.data.height = Math.max(5, newH)
    render()
  } else if (isDrawing.value && currentRect.value) {
    currentRect.value.width = imgX - startX.value
    currentRect.value.height = imgY - startY.value
    render()
  } else if (activeTool.value === 'bbox') {
    // Update cursor based on hover position
    let cursor = 'crosshair'

    // Check selected annotation first
    if (selectedAnnotation.value !== null) {
      const anno = annotations.value[selectedAnnotation.value]
      const edge = getEdgeAtPoint(anno, imgX, imgY)
      if (edge) {
        cursor = getCursorForEdge(edge)
      }
    }

    // Then check all annotations
    if (cursor === 'crosshair') {
      for (let i = annotations.value.length - 1; i >= 0; i--) {
        const anno = annotations.value[i]
        const edge = getEdgeAtPoint(anno, imgX, imgY)
        if (edge) {
          cursor = getCursorForEdge(edge)
          break
        }
      }
    }

    canvas.value.style.cursor = cursor
  }
}

function handleMouseUp(e) {
  if (isPanning.value) {
    isPanning.value = false
    canvas.value.style.cursor = 'default'
  } else if (isMoving.value) {
    isMoving.value = false
    dragStartAnno.value = null
    canvas.value.style.cursor = 'crosshair'
    saveHistory()
  } else if (isResizing.value) {
    isResizing.value = false
    resizeEdge.value = null
    dragStartAnno.value = null
    canvas.value.style.cursor = 'crosshair'
    saveHistory()
  } else if (isDrawing.value && currentRect.value) {
    isDrawing.value = false

    // Normalize rect (handle negative width/height)
    let { x, y, width, height } = currentRect.value
    if (width < 0) {
      x += width
      width = -width
    }
    if (height < 0) {
      y += height
      height = -height
    }

    // Only add if rect is big enough
    if (width > 5 && height > 5) {
      const annotation = {
        label_class_id: activeClass.value,
        annotation_type: 'bbox',
        data: { x, y, width, height }
      }
      annotations.value.push(annotation)
      selectedAnnotation.value = annotations.value.length - 1 // Auto-select new annotation
      saveHistory()
    }

    currentRect.value = null
    render()
  }
}

function handleWheel(e) {
  e.preventDefault()
  const rect = canvas.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  const delta = e.deltaY > 0 ? 0.9 : 1.1
  const newScale = Math.max(0.1, Math.min(5, scale.value * delta))

  // Zoom towards cursor
  const wx = (x - offsetX.value) / scale.value
  const wy = (y - offsetY.value) / scale.value

  scale.value = newScale
  offsetX.value = x - wx * scale.value
  offsetY.value = y - wy * scale.value

  render()
}

// Keyboard handler
function handleKeydown(e) {
  // Tool shortcuts
  const keyMap = { 'v': 'select', 'b': 'bbox', 'h': 'pan', 'z': 'zoom' }
  if (!e.ctrlKey && !e.metaKey && keyMap[e.key.toLowerCase()]) {
    activeTool.value = keyMap[e.key.toLowerCase()]
    return
  }

  // Class shortcuts
  const cls = classes.value.find(c => c.shortcut_key === e.key)
  if (cls) {
    selectClass(cls.id)
    return
  }

  // Undo/Redo
  if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
    e.preventDefault()
    undo()
  }
  if ((e.ctrlKey || e.metaKey) && e.key === 'y') {
    e.preventDefault()
    redo()
  }

  // Save
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    save()
  }

  // Delete selected
  if (e.key === 'Delete' || e.key === 'Backspace') {
    if (selectedAnnotation.value !== null) {
      deleteAnnotation(selectedAnnotation.value)
    }
  }

  // Navigation
  if (e.key === 'ArrowLeft') prevImage()
  if (e.key === 'ArrowRight') nextImage()
}

// Annotation management
function selectAnnotationAt(x, y) {
  for (let i = annotations.value.length - 1; i >= 0; i--) {
    const anno = annotations.value[i]
    const d = anno.data
    if (x >= d.x && x <= d.x + d.width && y >= d.y && y <= d.y + d.height) {
      selectedAnnotation.value = i
      render()
      return
    }
  }
  selectedAnnotation.value = null
  render()
}

function selectAnnotation(idx) {
  selectedAnnotation.value = idx
  render()
}

function selectClass(classId) {
  activeClass.value = classId
  // If an annotation is selected, update its class
  if (selectedAnnotation.value !== null) {
    annotations.value[selectedAnnotation.value].label_class_id = classId
    saveHistory()
    render()
  }
}

function deleteAnnotation(idx) {
  annotations.value.splice(idx, 1)
  selectedAnnotation.value = null
  saveHistory()
  render()
}

// History
function saveHistory() {
  history.value = history.value.slice(0, historyIndex.value + 1)
  history.value.push(JSON.stringify(annotations.value))
  historyIndex.value = history.value.length - 1
}

function undo() {
  if (historyIndex.value > 0) {
    historyIndex.value--
    annotations.value = JSON.parse(history.value[historyIndex.value])
    render()
  }
}

function redo() {
  if (historyIndex.value < history.value.length - 1) {
    historyIndex.value++
    annotations.value = JSON.parse(history.value[historyIndex.value])
    render()
  }
}

// Save
async function save() {
  saving.value = true
  try {
    // Get current user's username from localStorage
    const username = localStorage.getItem(`project_${projectId}_username`)

    await axios.post(`/api/annotations/image/${imageId.value}`, {
      annotations: annotations.value,
      annotated_by: username
    })
    // Update image status
    await axios.put(`/api/images/${imageId.value}/status`, {
      status: 'annotated'
    })
  } catch (error) {
    alert('Save failed: ' + error.message)
  } finally {
    saving.value = false
  }
}

// Navigation
async function prevImage() {
  if (currentIndex.value > 0) {
    await save()
    currentIndex.value--
    imageId.value = imageList.value[currentIndex.value].id
    router.replace(`/annotate/${projectId}/${imageId.value}`)
    await loadImage()
  }
}

async function nextImage() {
  if (currentIndex.value < imageList.value.length - 1) {
    await save()
    currentIndex.value++
    imageId.value = imageList.value[currentIndex.value].id
    router.replace(`/annotate/${projectId}/${imageId.value}`)
    await loadImage()
  }
}

// Helpers
function getClassName(classId) {
  return classes.value.find(c => c.id === classId)?.name || 'Unknown'
}

function getClassColor(classId) {
  return classes.value.find(c => c.id === classId)?.color || '#999'
}
</script>

<style scoped>
.annotate {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 56px);
  background: #1a1a1a;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 1rem;
  background: #333;
  color: white;
  flex-shrink: 0;
}

.tool-group {
  display: flex;
  gap: 0.25rem;
}

.tool-group button {
  padding: 0.5rem 0.75rem;
  border: none;
  background: #555;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.tool-group button:hover {
  background: #666;
}

.tool-group button.active {
  background: #4CAF50;
}

.tool-group button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.save-btn {
  background: #4CAF50 !important;
}

.nav-group {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-group button {
  padding: 0.5rem 0.75rem;
  border: none;
  background: #555;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

.nav-group button:hover:not(:disabled) {
  background: #666;
}

.nav-group button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-info {
  min-width: 80px;
  text-align: center;
}

.workspace {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.canvas-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.canvas-container canvas {
  display: block;
  cursor: crosshair;
}

.sidebar {
  width: 280px;
  background: #2a2a2a;
  color: white;
  overflow-y: auto;
  flex-shrink: 0;
}

.classes-panel,
.annotations-panel,
.info-panel {
  padding: 1rem;
  border-bottom: 1px solid #444;
}

.classes-panel h3,
.annotations-panel h3,
.info-panel h3 {
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
  color: #aaa;
  font-weight: normal;
}

.empty-hint {
  color: #666;
  font-size: 0.875rem;
  font-style: italic;
}

.empty-hint.info {
  color: #4CAF50;
  background: rgba(76, 175, 80, 0.1);
  padding: 0.75rem;
  border-radius: 4px;
  border: 1px solid rgba(76, 175, 80, 0.3);
  font-style: normal;
  line-height: 1.5;
}

.class-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 0.25rem;
}

.class-item:hover {
  background: #3a3a3a;
}

.class-item.active {
  background: #4CAF50;
}

.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.class-name {
  flex: 1;
  font-size: 0.875rem;
}

.shortcut {
  background: #444;
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
  font-size: 0.75rem;
  font-family: monospace;
}

.annotation-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 0.25rem;
}

.annotation-item:hover {
  background: #3a3a3a;
}

.annotation-item.selected {
  background: #4a4a4a;
  outline: 1px solid #4CAF50;
}

.anno-label {
  flex: 1;
  font-size: 0.875rem;
}

.delete-btn {
  border: none;
  background: none;
  cursor: pointer;
  opacity: 0.5;
  padding: 0.25rem;
}

.delete-btn:hover {
  opacity: 1;
}

.info-panel .info-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.info-panel .info-item span:first-child {
  color: #888;
}
</style>
