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
        <button @click="undo" title="Undo (Ctrl+Z)">↶</button>
        <button @click="redo" title="Redo (Ctrl+Y)">↷</button>
      </div>
      <div class="tool-group">
        <button @click="save" class="save-btn">💾 {{ $t('annotate.save') }}</button>
      </div>
      <div class="nav-group">
        <button @click="prevImage">◀ {{ $t('annotate.prev') }}</button>
        <span>{{ currentIndex + 1 }} / {{ totalImages }}</span>
        <button @click="nextImage">{{ $t('annotate.next') }} ▶</button>
      </div>
    </div>

    <div class="workspace">
      <div class="canvas-container">
        <canvas ref="canvas"></canvas>
      </div>

      <div class="sidebar">
        <div class="classes-panel">
          <h3>{{ $t('annotate.classes') }}</h3>
          <div
            v-for="cls in classes"
            :key="cls.id"
            :class="{ active: activeClass === cls.id }"
            class="class-item"
            @click="activeClass = cls.id"
          >
            <span class="color-dot" :style="{ background: cls.color }"></span>
            {{ cls.name }}
          </div>
        </div>

        <div class="annotations-panel">
          <h3>{{ $t('annotate.annotations') }}</h3>
          <div
            v-for="anno in annotations"
            :key="anno.id"
            class="annotation-item"
          >
            <span class="color-dot" :style="{ background: anno.color }"></span>
            {{ anno.class_name }}
            <button @click="deleteAnnotation(anno.id)">🗑</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()
const projectId = route.params.projectId
const imageId = ref(route.params.imageId)

const canvas = ref(null)
const activeTool = ref('bbox')
const activeClass = ref(null)
const classes = ref([])
const annotations = ref([])
const currentIndex = ref(0)
const totalImages = ref(0)

const tools = [
  { id: 'select', name: t('annotate.select'), icon: '👆', key: 'D' },
  { id: 'bbox', name: t('annotate.bbox'), icon: '⬜', key: 'B' },
  { id: 'polygon', name: t('annotate.polygon'), icon: '⬡', key: 'P' },
  { id: 'brush', name: t('annotate.brush'), icon: '🖌', key: 'U' },
  { id: 'zoom', name: t('annotate.zoom'), icon: '🔍', key: 'Z' }
]

function handleKeydown(e) {
  const keyMap = {
    'd': 'select',
    'b': 'bbox',
    'p': 'polygon',
    'u': 'brush',
    'z': 'zoom'
  }

  if (!e.ctrlKey && keyMap[e.key.toLowerCase()]) {
    activeTool.value = keyMap[e.key.toLowerCase()]
  }

  if (e.ctrlKey && e.key === 'z') {
    undo()
  }
  if (e.ctrlKey && e.key === 'y') {
    redo()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  // TODO: Initialize canvas, load image, fetch annotations
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

function undo() {
  // TODO: Implement undo
}

function redo() {
  // TODO: Implement redo
}

function save() {
  // TODO: Save annotations
}

function prevImage() {
  // TODO: Navigate to previous image
}

function nextImage() {
  // TODO: Navigate to next image
}

function deleteAnnotation(id) {
  // TODO: Delete annotation
}
</script>

<style scoped>
.annotate {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 56px);
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 1rem;
  background: #333;
  color: white;
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
}

.tool-group button.active {
  background: #4CAF50;
}

.tool-group button:hover {
  background: #666;
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

.workspace {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.canvas-container {
  flex: 1;
  background: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar {
  width: 280px;
  background: white;
  border-left: 1px solid #ddd;
  overflow-y: auto;
}

.classes-panel,
.annotations-panel {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.classes-panel h3,
.annotations-panel h3 {
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
  color: #666;
}

.class-item,
.annotation-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}

.class-item:hover,
.class-item.active {
  background: #f0f0f0;
}

.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.annotation-item button {
  margin-left: auto;
  border: none;
  background: none;
  cursor: pointer;
  opacity: 0.5;
}

.annotation-item:hover button {
  opacity: 1;
}
</style>
