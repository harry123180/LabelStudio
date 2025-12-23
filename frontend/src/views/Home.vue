<template>
  <div class="home">
    <div class="hero">
      <h1>{{ $t('home.welcome') }}</h1>
      <p>{{ $t('home.description') }}</p>
      <div class="actions">
        <router-link to="/projects" class="btn btn-primary">
          {{ $t('home.getStarted') }}
        </router-link>
      </div>
    </div>

    <div class="about-section">
      <h2>關於 LabelStudio</h2>
      <p class="intro">
        LabelStudio 是一款專為課堂教學設計的輕量級圖片標註工具，讓學生可以輕鬆學習機器學習資料標註的流程。
      </p>

      <div class="feature-list">
        <div class="feature-item">
          <span class="check">✓</span>
          <span>支援矩形框 (Bounding Box) 標註</span>
        </div>
        <div class="feature-item">
          <span class="check">✓</span>
          <span>團隊協作 - 成員任務分配與進度追蹤</span>
        </div>
        <div class="feature-item">
          <span class="check">✓</span>
          <span>手機 QR Code 掃描上傳圖片</span>
        </div>
        <div class="feature-item">
          <span class="check">✓</span>
          <span>匯出 YOLO、COCO、Pascal VOC 格式</span>
        </div>
        <div class="feature-item">
          <span class="check">✓</span>
          <span>資料集自動分割 (Train/Val/Test)</span>
        </div>
        <div class="feature-item">
          <span class="check">✓</span>
          <span>可打包成 Windows 執行檔，無需安裝</span>
        </div>
      </div>
    </div>

    <div class="github-section">
      <div class="github-card">
        <div class="github-icon">
          <svg height="48" viewBox="0 0 16 16" width="48">
            <path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
          </svg>
        </div>
        <div class="github-content">
          <h3>開源專案</h3>
          <p>如果這個工具對你有幫助，歡迎到 GitHub 給我們一顆星星！</p>
          <a href="https://github.com/harry123180/LabelStudio" target="_blank" class="github-link">
            <span class="star">⭐</span>
            Star on GitHub
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.hero {
  text-align: center;
  padding: 4rem 2rem;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
  border-radius: 12px;
  margin-bottom: 2rem;
}

.hero h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.25rem;
  opacity: 0.9;
  margin-bottom: 2rem;
}

.btn {
  display: inline-block;
  padding: 0.75rem 2rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background: #45a049;
  transform: translateY(-2px);
}

.about-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.about-section h2 {
  margin-bottom: 1rem;
  color: #333;
}

.intro {
  font-size: 1.1rem;
  color: #555;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
}

.feature-item .check {
  color: #4CAF50;
  font-size: 1.25rem;
  font-weight: bold;
}

.feature-item span:last-child {
  color: #444;
}

.github-section {
  margin-top: 2rem;
}

.github-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 2rem;
  background: linear-gradient(135deg, #24292e 0%, #1a1e22 100%);
  color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.github-icon {
  flex-shrink: 0;
}

.github-icon svg {
  color: white;
}

.github-content h3 {
  margin-bottom: 0.5rem;
  font-size: 1.25rem;
}

.github-content p {
  opacity: 0.9;
  margin-bottom: 1rem;
}

.github-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.25rem;
  background: #238636;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 600;
  transition: all 0.2s;
}

.github-link:hover {
  background: #2ea043;
  transform: translateY(-2px);
}

.github-link .star {
  font-size: 1.1rem;
}

@media (max-width: 600px) {
  .github-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>
