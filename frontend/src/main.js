/**
 * LabelStudio Frontend Entry Point
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import router from './router'

// i18n messages
import zhTW from './locales/zh-TW.json'
import en from './locales/en.json'

// Create i18n instance
const i18n = createI18n({
  legacy: false,
  locale: 'zh-TW', // Default: Traditional Chinese
  fallbackLocale: 'en',
  messages: {
    'zh-TW': zhTW,
    'en': en
  }
})

// Create app
const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

app.mount('#app')
