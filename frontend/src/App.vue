<template>
  <div id="app">
    <nav class="navbar">
      <div class="navbar-brand">
        <router-link to="/">LabelStudio</router-link>
      </div>
      <div class="navbar-menu">
        <router-link to="/projects">{{ $t('nav.projects') }}</router-link>
      </div>
      <div class="navbar-end">
        <LanguageSwitcher />
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans TC', sans-serif;
  background-color: #f5f5f5;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  display: flex;
  align-items: center;
  padding: 0 1rem;
  height: 56px;
  background: #1a1a2e;
  color: white;
}

.navbar-brand a {
  font-size: 1.25rem;
  font-weight: bold;
  color: white;
  text-decoration: none;
}

.navbar-menu {
  flex: 1;
  margin-left: 2rem;
}

.navbar-menu a {
  color: #ccc;
  text-decoration: none;
  margin-right: 1rem;
}

.navbar-menu a:hover,
.navbar-menu a.router-link-active {
  color: white;
}

.navbar-end {
  display: flex;
  align-items: center;
}

.main-content {
  flex: 1;
  padding: 1rem;
}
</style>
