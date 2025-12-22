# LabelStudio

一個專為課堂教學設計的輕量級圖片標註工具，讓學員能在區域網路內協同進行資料標註。

## 專案動機

[Roboflow](https://roboflow.com) 是優秀的圖片標註與訓練 SaaS 平台，但註冊限制多、依賴外網。本專案目標是打造一個**可離線部署、適合教學情境**的替代方案。

## 技術架構

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (Vue 3)                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │ Canvas 標註  │ │  專案管理   │ │   團隊協作介面   │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘│
└─────────────────────────────────────────────────────────┘
                           │ REST API
┌─────────────────────────────────────────────────────────┐
│                    Backend (Flask)                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │  標註服務    │ │  用戶認證   │ │   檔案管理      │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘│
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│              Storage (SQLite + File System)             │
└─────────────────────────────────────────────────────────┘
```

## 核心功能規劃

### 1. 標註工具 (參考 Roboflow Annotate)

| 工具 | 快捷鍵 | 說明 |
|------|--------|------|
| **Bounding Box** | `B` | 矩形框標註，用於物件偵測 |
| **Polygon** | `P` | 多邊形標註，用於精確輪廓 |
| **Brush/Mask** | `U` | 筆刷遮罩，用於語意分割 |
| **Drag/Select** | `D` | 選取、移動、調整標註大小 |
| **Zoom** | `Z` / 滾輪 | 放大縮小畫布 |
| **Undo/Redo** | `Ctrl+Z` / `Ctrl+Y` | 復原與重做 |

### 2. 專案管理

- **專案建立**：教師可建立標註專案，定義類別 (Ontology)
- **圖片上傳**：支援批次上傳 JPG、PNG、BMP 等格式
- **資料集分割**：自動或手動分配 Train / Validation / Test
- **類別管理**：新增、編輯、刪除標註類別，支援顏色設定

### 3. 團隊協作 (教學情境)

- **角色權限**
  - `教師 (Admin)`：建立專案、管理類別、審核標註、匯出資料
  - `學員 (Labeler)`：執行標註任務
  - `審核者 (Reviewer)`：檢查標註品質

- **任務分配**：將圖片分配給不同學員標註
- **進度追蹤**：即時查看各學員標註進度
- **標註歷史**：記錄每張圖片的修改歷史
- **評論功能**：教師可對標註給予回饋

### 4. 手機掃碼上傳 (QR Code)

專為課堂設計的快速圖片收集功能，學員用手機掃碼即可上傳圖片。

#### 使用流程

```
┌─────────────────────────────────────────────────────────────┐
│  教師端 (電腦)                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  專案: 貓狗辨識                    [ 顯示 QR Code ]  │   │
│  │                                                      │   │
│  │     ┌──────────────┐                                │   │
│  │     │ ▄▄▄▄▄▄▄▄▄▄▄ │   掃描加入：                    │   │
│  │     │ █         █ │   http://192.168.1.100:5000     │   │
│  │     │ █  QR碼   █ │   /upload/proj_abc123           │   │
│  │     │ █         █ │                                 │   │
│  │     │ ▀▀▀▀▀▀▀▀▀▀▀ │   已上傳: 47 張                 │   │
│  │     └──────────────┘   在線學員: 12 人               │   │
│  │                                                      │   │
│  │  [ 複製連結 ]  [ 下載 QR Code ]  [ 全螢幕顯示 ]      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 掃碼
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  學員端 (手機瀏覽器)                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │              📷                              │    │   │
│  │  │                                              │    │   │
│  │  │         點擊拍照或選擇相簿                    │    │   │
│  │  │                                              │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │                                                      │   │
│  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐                       │   │
│  │  │ 🖼 │ │ 🖼 │ │ 🖼 │ │ +  │  已選 3 張            │   │
│  │  └────┘ └────┘ └────┘ └────┘                       │   │
│  │                                                      │   │
│  │  暱稱: [  王小明  ]                                  │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │              上傳 (3 張)                     │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### 功能特點

- **免登入上傳**：學員只需輸入暱稱，無需註冊帳號
- **批次選擇**：支援一次選擇多張照片上傳
- **即時拍照**：可直接啟動相機拍攝
- **上傳進度**：顯示上傳進度與成功/失敗狀態
- **自動壓縮**：手機端自動壓縮大圖，加速上傳
- **來源追蹤**：記錄每張圖片的上傳者，方便後續分配標註任務

#### 技術實現

```python
# backend/app/routes/qrcode.py
import qrcode
import io
import base64
from flask import Blueprint, jsonify, request, current_app
from app.utils.network import get_local_ip

qr_bp = Blueprint('qrcode', __name__)

@qr_bp.route('/api/projects/<project_id>/qrcode')
def generate_qr(project_id):
    """生成專案上傳頁面的 QR Code"""
    local_ip = get_local_ip()
    port = current_app.config.get('PORT', 5000)

    # 上傳頁面 URL
    upload_url = f"http://{local_ip}:{port}/upload/{project_id}"

    # 生成 QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(upload_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # 轉為 base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return jsonify({
        'qrcode': f'data:image/png;base64,{img_base64}',
        'url': upload_url,
        'project_id': project_id
    })


@qr_bp.route('/api/projects/<project_id>/quick-upload', methods=['POST'])
def quick_upload(project_id):
    """手機端快速上傳 (免登入)"""
    nickname = request.form.get('nickname', '匿名')
    files = request.files.getlist('images')

    uploaded = []
    for file in files:
        if file and allowed_file(file.filename):
            # 儲存圖片
            filename = save_uploaded_file(file, project_id)
            uploaded.append({
                'filename': filename,
                'uploader': nickname,
                'source': 'mobile'
            })

    return jsonify({
        'success': True,
        'uploaded': len(uploaded),
        'files': uploaded
    })
```

```vue
<!-- frontend/src/views/MobileUpload.vue -->
<template>
  <div class="mobile-upload">
    <h2>{{ projectName }}</h2>

    <!-- 拍照/選擇區域 -->
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
        <p>點擊拍照或選擇相簿</p>
      </div>
    </div>

    <!-- 預覽已選圖片 -->
    <div class="preview-grid">
      <div v-for="(img, idx) in selectedImages" :key="idx" class="preview-item">
        <img :src="img.preview" />
        <button @click="removeImage(idx)">✕</button>
      </div>
    </div>

    <!-- 暱稱輸入 -->
    <input v-model="nickname" placeholder="輸入你的暱稱" class="nickname-input" />

    <!-- 上傳按鈕 -->
    <button
      class="upload-btn"
      :disabled="selectedImages.length === 0 || uploading"
      @click="upload"
    >
      {{ uploading ? `上傳中 ${progress}%` : `上傳 (${selectedImages.length} 張)` }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { compressImage } from '@/utils/imageCompress'

const selectedImages = ref([])
const nickname = ref('')
const uploading = ref(false)
const progress = ref(0)

async function handleFiles(e) {
  const files = Array.from(e.target.files)

  for (const file of files) {
    // 壓縮圖片 (限制最大 1920px，品質 0.8)
    const compressed = await compressImage(file, 1920, 0.8)
    selectedImages.value.push({
      file: compressed,
      preview: URL.createObjectURL(compressed)
    })
  }
}

async function upload() {
  uploading.value = true
  const formData = new FormData()
  formData.append('nickname', nickname.value || '匿名')

  selectedImages.value.forEach(img => {
    formData.append('images', img.file)
  })

  // 使用 XMLHttpRequest 追蹤進度
  const xhr = new XMLHttpRequest()
  xhr.upload.onprogress = (e) => {
    progress.value = Math.round((e.loaded / e.total) * 100)
  }

  xhr.onload = () => {
    uploading.value = false
    selectedImages.value = []
    alert('上傳成功！')
  }

  xhr.open('POST', `/api/projects/${projectId}/quick-upload`)
  xhr.send(formData)
}
</script>
```

#### 圖片壓縮工具

```javascript
// frontend/src/utils/imageCompress.js
export async function compressImage(file, maxSize = 1920, quality = 0.8) {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        let { width, height } = img

        // 等比例縮放
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
```

#### 教室使用場景

```
1. 教師建立專案「校園植物辨識」
2. 點擊「顯示 QR Code」，投影到教室螢幕
3. 學生手機連接教室 WiFi
4. 掃描 QR Code，進入上傳頁面
5. 學生在校園拍攝植物照片，直接上傳
6. 教師端即時看到上傳數量增加
7. 收集完成後，分配標註任務給各組學生
```

### 5. 資料匯出

支援主流格式匯出：

| 格式 | 用途 |
|------|------|
| **COCO JSON** | Detectron2、MMDetection |
| **YOLO TXT** | YOLOv5、YOLOv8、YOLO11 |
| **Pascal VOC XML** | 傳統物件偵測 |
| **CreateML JSON** | Apple Core ML |
| **CSV** | 自定義處理 |

### 5. 資料集分割與管理

#### 分割比例設定

```
┌─────────────────────────────────────────────────────────┐
│  資料集分割設定                                          │
├─────────────────────────────────────────────────────────┤
│  Training    [=============================] 70%  ◀──┐ │
│  Validation  [=========]                    20%     │ │
│  Test        [===]                          10%     │ │
├─────────────────────────────────────────────────────────┤
│  總計: 1000 張    ○ 隨機分配  ● 依序分配               │
│                                                         │
│  [ 重新分配 ]  [ 預覽分配結果 ]                         │
└─────────────────────────────────────────────────────────┘
```

- **自訂比例**：拖曳滑桿或輸入百分比 (如 80/10/10、70/20/10)
- **分配策略**：隨機分配 / 依序分配 / 分層抽樣 (按類別平衡)
- **手動調整**：可將單張圖片拖曳至不同分割區
- **鎖定機制**：已標註的圖片可鎖定分割，避免重新分配時被移動

### 6. 資料增強 (Data Augmentation)

匯出時可選擇套用資料增強，擴充訓練資料集。

#### 增強選項

| 類別 | 增強方式 | 參數 | 說明 |
|------|----------|------|------|
| **幾何變換** | 水平翻轉 | - | 左右鏡像 |
| | 垂直翻轉 | - | 上下鏡像 |
| | 旋轉 | -45° ~ +45° | 隨機角度旋轉 |
| | 縮放 | 0.5x ~ 1.5x | 隨機縮放比例 |
| | 裁切 | 0% ~ 30% | 隨機裁切邊緣 |
| | 平移 | -20% ~ +20% | 隨機位移 |
| | 傾斜 | -15° ~ +15° | 透視變形 |
| **色彩調整** | 亮度 | -30% ~ +30% | 調整明暗 |
| | 對比度 | 0.7x ~ 1.3x | 調整對比 |
| | 飽和度 | 0.7x ~ 1.3x | 調整色彩鮮豔度 |
| | 色相偏移 | -20° ~ +20° | 色調微調 |
| | 灰階 | 機率 0~100% | 隨機轉灰階 |
| **噪點與模糊** | 高斯噪點 | σ: 0 ~ 25 | 加入隨機雜訊 |
| | 椒鹽噪點 | 密度: 0 ~ 5% | 黑白點雜訊 |
| | 高斯模糊 | 半徑: 0 ~ 3px | 模糊效果 |
| | 動態模糊 | 強度: 0 ~ 7px | 模擬運動模糊 |
| **進階** | Mosaic | 4/9 格 | 拼貼多張圖片 (YOLO 風格) |
| | Mixup | α: 0.2 ~ 0.5 | 圖片混合 |
| | Cutout | 遮罩數: 1~5 | 隨機遮擋區塊 |

#### 增強設定介面

```
┌─────────────────────────────────────────────────────────┐
│  資料增強設定                          [ 即時預覽 ]      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ☑ 水平翻轉        機率: [===●=====] 50%               │
│  ☑ 旋轉            範圍: [-15°] ~ [+15°]               │
│  ☑ 縮放            範圍: [0.8x] ~ [1.2x]               │
│  ☐ 垂直翻轉                                            │
│  ☑ 亮度調整        範圍: [-20%] ~ [+20%]               │
│  ☑ 高斯噪點        σ: [=●========] 10                  │
│  ☐ 動態模糊                                            │
│  ☐ Mosaic                                              │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  每張原圖生成: [  3  ] 張增強圖片                        │
│  預估總量: 原始 500 張 → 增強後 2000 張                  │
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │  原圖    │ │ 增強 #1  │ │ 增強 #2  │ │ 增強 #3  │   │
│  │  [IMG]   │ │  [IMG]   │ │  [IMG]   │ │  [IMG]   │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────┘
```

#### 技術實現 (Pillow / OpenCV)

```python
# backend/app/services/augmentation.py
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import random

class Augmentor:
    """資料增強器"""

    def __init__(self, config: dict):
        self.config = config

    def augment(self, image: np.ndarray, annotations: list) -> tuple:
        """
        套用增強並同步調整標註座標

        Args:
            image: OpenCV 格式圖片 (BGR)
            annotations: 標註列表 [{"bbox": [x,y,w,h], "class": "cat"}, ...]

        Returns:
            (augmented_image, adjusted_annotations)
        """
        img = image.copy()
        annos = [a.copy() for a in annotations]

        # 幾何變換 (需同步調整標註)
        if self.config.get('horizontal_flip') and random.random() < 0.5:
            img, annos = self._horizontal_flip(img, annos)

        if self.config.get('rotation'):
            angle = random.uniform(*self.config['rotation_range'])
            img, annos = self._rotate(img, annos, angle)

        if self.config.get('scale'):
            factor = random.uniform(*self.config['scale_range'])
            img, annos = self._scale(img, annos, factor)

        # 色彩調整 (不影響標註)
        if self.config.get('brightness'):
            img = self._adjust_brightness(img, self.config['brightness_range'])

        if self.config.get('gaussian_noise'):
            img = self._add_gaussian_noise(img, self.config['noise_sigma'])

        return img, annos

    def _horizontal_flip(self, img, annos):
        """水平翻轉"""
        h, w = img.shape[:2]
        img = cv2.flip(img, 1)

        for anno in annos:
            x, y, bw, bh = anno['bbox']
            anno['bbox'] = [w - x - bw, y, bw, bh]

        return img, annos

    def _rotate(self, img, annos, angle):
        """旋轉圖片與標註"""
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        img = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)

        # 旋轉標註框 (簡化：重新計算外接矩形)
        for anno in annos:
            anno['bbox'] = self._rotate_bbox(anno['bbox'], M, w, h)

        return img, annos

    def _add_gaussian_noise(self, img, sigma):
        """加入高斯噪點"""
        noise = np.random.normal(0, sigma, img.shape).astype(np.float32)
        noisy = np.clip(img.astype(np.float32) + noise, 0, 255)
        return noisy.astype(np.uint8)

    def _adjust_brightness(self, img, range_):
        """調整亮度"""
        factor = random.uniform(*range_)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * (1 + factor), 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
```

#### 增強策略建議

| 應用場景 | 建議增強組合 |
|----------|-------------|
| **物件偵測 (一般)** | 翻轉 + 旋轉±15° + 縮放0.8~1.2x + 亮度±20% |
| **小物件偵測** | 上述 + 隨機裁切 + Mosaic |
| **光線變化大** | 亮度±40% + 對比度 + 高斯噪點 |
| **戶外場景** | 動態模糊 + 色相偏移 + 飽和度 |
| **醫療影像** | 僅幾何變換，避免色彩調整 |

## 開發階段規劃

### Phase 1：基礎架構
- [ ] Flask 後端 API 框架
- [ ] Vue 3 前端專案建立
- [ ] SQLite 資料庫設計
- [ ] 使用者認證系統 (簡易帳號密碼)

### Phase 2：核心標註功能
- [ ] Canvas 畫布渲染
- [ ] Bounding Box 標註工具
- [ ] Polygon 標註工具
- [ ] 標註資料 CRUD API

### Phase 3：專案管理
- [ ] 專案建立與設定
- [ ] 圖片上傳與管理
- [ ] 類別 (Class) 管理

### Phase 4：協作功能
- [ ] 多用戶支援
- [ ] 任務分配系統
- [ ] 進度統計儀表板
- [ ] QR Code 生成 (qrcode 庫)
- [ ] 手機上傳頁面 (響應式設計)
- [ ] 圖片壓縮上傳
- [ ] 即時上傳統計

### Phase 5：匯出與整合
- [ ] 多格式匯出 (COCO、YOLO、VOC、CreateML)
- [ ] 匯出前預覽與驗證

### Phase 6：資料集管理與增強
- [ ] 資料集分割介面 (Train/Val/Test 比例調整)
- [ ] 分配策略 (隨機/依序/分層抽樣)
- [ ] 基礎增強 (翻轉、旋轉、縮放)
- [ ] 色彩增強 (亮度、對比度、飽和度)
- [ ] 噪點與模糊 (高斯噪點、動態模糊)
- [ ] 進階增強 (Mosaic、Mixup、Cutout)
- [ ] 增強即時預覽
- [ ] 標註座標同步調整

### Phase 7：打包與部署
- [ ] Flask 整合 Vue 靜態文件服務
- [ ] PyInstaller 打包配置
- [ ] 啟動器 (自動顯示 IP、開啟瀏覽器)
- [ ] 一鍵建置腳本
- [ ] 系統托盤模式 (可選)

## 目錄結構

```
LabelStudio/
├── backend/                 # Flask 後端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/         # 資料模型
│   │   ├── routes/         # API 路由
│   │   ├── services/       # 業務邏輯
│   │   └── utils/          # 工具函數
│   ├── migrations/         # 資料庫遷移
│   ├── config.py
│   └── requirements.txt
│
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── components/    # 元件
│   │   ├── views/         # 頁面
│   │   ├── stores/        # Pinia 狀態管理
│   │   └── utils/         # 工具函數
│   ├── package.json
│   └── vite.config.js
│
├── scripts/               # 打包腳本
│   ├── build.py          # 自動化建置腳本
│   └── labelstudio.spec  # PyInstaller 配置
│
├── uploads/               # 上傳圖片儲存
├── exports/               # 匯出檔案暫存
└── README.md
```

## Windows 一鍵部署方案

### 設計目標

教師只需雙擊 `LabelStudio.exe`，即可在區網內啟動服務，學員瀏覽器輸入 IP 即可使用。

**不需要安裝**：Python、Node.js、資料庫

### 技術方案

```
┌─────────────────────────────────────────────────────────────┐
│                     打包流程                                 │
├─────────────────────────────────────────────────────────────┤
│  1. npm run build     →  Vue 編譯成 dist/ 靜態文件           │
│  2. Flask 整合靜態文件  →  單一 Python 應用服務前後端          │
│  3. PyInstaller 打包   →  生成 LabelStudio.exe              │
└─────────────────────────────────────────────────────────────┘

最終產物：
┌─────────────────────────┐
│  LabelStudio/           │
│  ├── LabelStudio.exe    │  ← 雙擊啟動
│  └── data/              │  ← 自動生成 (資料庫 + 上傳檔案)
└─────────────────────────┘
```

### 核心實現

#### 1. Flask 整合靜態前端

```python
# backend/app/__init__.py
from flask import Flask, send_from_directory
import os
import sys

def get_resource_path(relative_path):
    """取得資源路徑，支援 PyInstaller 打包"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包後的臨時目錄
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), '..', '..', relative_path)

def create_app():
    # 靜態文件路徑 (Vue 編譯產物)
    static_folder = get_resource_path('dist')

    app = Flask(__name__,
                static_folder=static_folder,
                static_url_path='')

    # 前端路由：所有非 API 請求返回 index.html (SPA)
    @app.route('/')
    @app.route('/<path:path>')
    def serve_frontend(path=''):
        if path.startswith('api/'):
            return {'error': 'Not Found'}, 404

        # 嘗試返回靜態文件，否則返回 index.html
        file_path = os.path.join(app.static_folder, path)
        if os.path.isfile(file_path):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')

    return app
```

#### 2. 主程式入口 (啟動器)

```python
# backend/main.py
import os
import sys
import socket
import webbrowser
import threading
from app import create_app

def get_local_ip():
    """取得本機區網 IP"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def get_data_dir():
    """取得資料目錄 (exe 同層級)"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包後
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(__file__)

    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def main():
    host = '0.0.0.0'
    port = 5000
    local_ip = get_local_ip()

    # 設定資料目錄
    data_dir = get_data_dir()
    os.environ['LABELSTUDIO_DATA_DIR'] = data_dir

    print("=" * 50)
    print("  LabelStudio 標註工具")
    print("=" * 50)
    print(f"  本機存取: http://localhost:{port}")
    print(f"  區網存取: http://{local_ip}:{port}")
    print(f"  資料目錄: {data_dir}")
    print("=" * 50)
    print("  按 Ctrl+C 停止服務")
    print("=" * 50)

    # 自動開啟瀏覽器
    threading.Timer(1.5, lambda: webbrowser.open(f'http://localhost:{port}')).start()

    # 啟動 Flask
    app = create_app()
    app.run(host=host, port=port, threaded=True)

if __name__ == '__main__':
    main()
```

#### 3. PyInstaller 打包配置

```python
# scripts/labelstudio.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../backend/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../dist', 'dist'),           # Vue 編譯產物
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'flask_sqlalchemy',
        'sqlalchemy',
        'PIL',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LabelStudio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                    # 壓縮執行檔
    console=True,                # 顯示控制台 (方便看 IP)
    icon='../assets/icon.ico',   # 應用圖示
)
```

#### 4. 一鍵建置腳本

```python
# scripts/build.py
import subprocess
import shutil
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def build():
    print("[1/4] 清理舊建置...")
    for folder in ['dist', 'build', 'output']:
        path = os.path.join(ROOT_DIR, folder)
        if os.path.exists(path):
            shutil.rmtree(path)

    print("[2/4] 建置前端...")
    frontend_dir = os.path.join(ROOT_DIR, 'frontend')
    subprocess.run(['npm', 'run', 'build'], cwd=frontend_dir, shell=True, check=True)

    # 將前端產物移到根目錄
    shutil.move(
        os.path.join(frontend_dir, 'dist'),
        os.path.join(ROOT_DIR, 'dist')
    )

    print("[3/4] 打包執行檔...")
    scripts_dir = os.path.join(ROOT_DIR, 'scripts')
    subprocess.run([
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'labelstudio.spec'
    ], cwd=scripts_dir, shell=True, check=True)

    print("[4/4] 整理輸出...")
    output_dir = os.path.join(ROOT_DIR, 'output')
    os.makedirs(output_dir, exist_ok=True)

    shutil.copy(
        os.path.join(scripts_dir, 'dist', 'LabelStudio.exe'),
        os.path.join(output_dir, 'LabelStudio.exe')
    )

    print("\n" + "=" * 50)
    print("建置完成！")
    print(f"執行檔位置: {os.path.join(output_dir, 'LabelStudio.exe')}")
    print("=" * 50)

if __name__ == '__main__':
    build()
```

### 建置環境需求 (僅開發者需要)

```bash
# 建置環境 (一次性設定)
pip install pyinstaller flask flask-cors flask-sqlalchemy pillow qrcode opencv-python
npm install  # 在 frontend 目錄

# 執行建置
python scripts/build.py
```

### 最終使用者體驗

```
1. 教師收到 LabelStudio.exe (約 30-50 MB)
2. 雙擊執行，控制台顯示區網 IP
3. 告知學員輸入 http://192.168.x.x:5000
4. 開始標註
5. 關閉視窗即停止服務
```

### 進階選項：系統托盤模式

如果不想顯示黑色控制台視窗，可使用 `pystray` 實現系統托盤：

```python
# 替代方案：托盤圖示 (進階)
# pip install pystray pillow

import pystray
from PIL import Image
import threading

def create_tray_icon(local_ip, port):
    # 建立托盤圖示
    icon_image = Image.new('RGB', (64, 64), color='#4CAF50')

    menu = pystray.Menu(
        pystray.MenuItem(f'區網: http://{local_ip}:{port}', None, enabled=False),
        pystray.MenuItem('開啟瀏覽器', lambda: webbrowser.open(f'http://localhost:{port}')),
        pystray.MenuItem('結束', lambda icon, item: icon.stop())
    )

    icon = pystray.Icon('LabelStudio', icon_image, 'LabelStudio', menu)
    return icon
```

## 快速開始

```bash
# 後端
cd backend
pip install -r requirements.txt
flask run --host=0.0.0.0

# 前端
cd frontend
npm install
npm run dev
```

學員透過區域網路存取 `http://<教師IP>:5173` 即可開始標註。

## 與 Roboflow 功能對比

| 功能 | Roboflow | LabelStudio (本專案) |
|------|----------|---------------------|
| **標註工具** | | |
| Bounding Box | ✅ | ✅ 計劃中 |
| Polygon | ✅ | ✅ 計劃中 |
| Brush/Mask | ✅ | ✅ 計劃中 |
| Smart Polygon (SAM) | ✅ | ❌ 暫不支援 |
| Auto Label | ✅ | ❌ 暫不支援 |
| **資料集管理** | | |
| Train/Val/Test 分割 | ✅ | ✅ 計劃中 |
| 自訂分割比例 | ✅ | ✅ 計劃中 |
| 分層抽樣 | ✅ | ✅ 計劃中 |
| **資料增強** | | |
| 幾何變換 (翻轉/旋轉/縮放) | ✅ | ✅ 計劃中 |
| 色彩調整 (亮度/對比/飽和) | ✅ | ✅ 計劃中 |
| 噪點/模糊 | ✅ | ✅ 計劃中 |
| Mosaic/Mixup/Cutout | ✅ | ✅ 計劃中 |
| 增強倍數設定 | ✅ 最多 50x | ✅ 計劃中 |
| 即時預覽 | ✅ | ✅ 計劃中 |
| **協作與部署** | | |
| 團隊協作 | ✅ | ✅ 計劃中 |
| QR Code 手機上傳 | ❌ | ✅ 計劃中 |
| 免登入快速上傳 | ❌ | ✅ 計劃中 |
| 雲端部署 | ✅ | ❌ 僅區網 |
| 離線使用 | ❌ | ✅ |
| 免費無限制 | ❌ | ✅ |
| 一鍵啟動 (exe) | ❌ | ✅ 計劃中 |
| 模型訓練 | ✅ | ❌ 不在範圍 |

## 授權

MIT License

## 參考資源

- [Roboflow Annotate](https://roboflow.com/annotate)
- [Roboflow Documentation](https://docs.roboflow.com/annotate/use-roboflow-annotate)
