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

    <div class="features">
      <div class="feature">
        <div class="icon">🏷️</div>
        <h3>{{ $t('annotate.bbox') }}</h3>
        <p>Bounding Box, Polygon, Brush</p>
      </div>
      <div class="feature">
        <div class="icon">👥</div>
        <h3>{{ $t('nav.projects') }}</h3>
        <p>Team collaboration</p>
      </div>
      <div class="feature">
        <div class="icon">📱</div>
        <h3>{{ $t('project.qrcode') }}</h3>
        <p>Mobile upload support</p>
      </div>
      <div class="feature">
        <div class="icon">📦</div>
        <h3>{{ $t('project.export') }}</h3>
        <p>YOLO, COCO, VOC formats</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.hero {
  text-align: center;
  padding: 4rem 2rem;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
  border-radius: 12px;
  margin-bottom: 3rem;
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

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.feature .icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature h3 {
  margin-bottom: 0.5rem;
  color: #333;
}

.feature p {
  color: #666;
}
</style>
