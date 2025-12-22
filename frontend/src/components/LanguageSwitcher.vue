<template>
  <div class="language-switcher">
    <button class="lang-btn" @click="toggleDropdown">
      🌐 {{ currentLangName }}
    </button>
    <div v-if="showDropdown" class="dropdown">
      <button
        v-for="lang in languages"
        :key="lang.code"
        :class="{ active: locale === lang.code }"
        @click="switchLanguage(lang.code)"
      >
        {{ lang.name }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()
const showDropdown = ref(false)

// Only Traditional Chinese and English (NO Simplified Chinese)
const languages = [
  { code: 'zh-TW', name: '繁體中文' },
  { code: 'en', name: 'English' }
]

const currentLangName = computed(() => {
  const lang = languages.find(l => l.code === locale.value)
  return lang ? lang.name : '繁體中文'
})

function toggleDropdown() {
  showDropdown.value = !showDropdown.value
}

function switchLanguage(code) {
  locale.value = code
  localStorage.setItem('locale', code)
  showDropdown.value = false
}
</script>

<style scoped>
.language-switcher {
  position: relative;
}

.lang-btn {
  background: transparent;
  border: 1px solid #555;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.lang-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  z-index: 100;
}

.dropdown button {
  display: block;
  width: 100%;
  padding: 0.75rem 1rem;
  border: none;
  background: white;
  text-align: left;
  cursor: pointer;
  font-size: 0.875rem;
}

.dropdown button:hover {
  background: #f0f0f0;
}

.dropdown button.active {
  background: #e0e0e0;
  font-weight: bold;
}
</style>
