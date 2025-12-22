# LabelStudio - Claude 記憶檔

此檔案記錄專案的核心設計原則，Claude 在協助開發時必須遵守。

---

## 語言規範 (最高優先級)

| 規則 | 說明 |
|------|------|
| **預設語言** | 繁體中文 (zh-TW) |
| **次要語言** | English (en) |
| **禁止語言** | 簡體中文 (zh-CN) ❌ **絕對禁止** |

### 適用範圍

- UI 介面文字：繁體中文 + 英文雙語
- 錯誤訊息：繁體中文 + 英文雙語
- 使用者提示：繁體中文 + 英文雙語
- README / 文件：繁體中文為主
- 程式碼註解：英文為主
- Git commit message：英文

### 目標用戶

- 台灣學生 (繁體中文)
- 外籍生 (English)

### i18n 實作

```
frontend/src/locales/
├── zh-TW.json   ← 繁體中文 (預設)
└── en.json      ← English
```

**永遠不要創建 zh-CN.json 或任何簡體中文資源**

---

## 專案概述

- **用途**：課堂教學用圖片標註工具
- **部署方式**：區域網路內，打包成 Windows exe
- **技術棧**：Vue 3 + Flask + SQLite

---

## 核心功能

1. 標註工具 (Bounding Box, Polygon, Brush)
2. 團隊協作 (教師/學員角色)
3. QR Code 手機掃碼上傳
4. 資料集分割與增強
5. 多格式匯出 (COCO, YOLO, VOC)

---

## Skills 目錄 (AI Agents 調用)

`skills/` 目錄包含可供 AI Agents 調用的 Python 腳本。

### 可用的 Skills

| Skill | 說明 |
|-------|------|
| `DatasetSkill` | 資料集管理：分割、統計、列表 |
| `AnnotationSkill` | 標註操作：建立、批次、驗證 |
| `ExportSkill` | 匯出操作：多格式、預覽 |
| `AugmentationSkill` | 資料增強：預設、預覽、估算 |

### 使用方式

```python
from skills import DatasetSkill

skill = DatasetSkill()
info = skill.get_info()  # 取得可用方法
result = skill.split_dataset(project_id=1, train=0.7, val=0.2, test=0.1)
```

### 設計原則

- 每個 Skill 都有 `get_info()` 方法供 Agent 發現功能
- 使用 `execute_in_context()` 在 Flask context 中執行
- 所有操作都會記錄 log

---

## 目錄結構

```
LabelStudio/
├── backend/         # Flask 後端
├── frontend/        # Vue 3 前端
├── skills/          # AI Agents 調用腳本 ⭐
├── scripts/         # 打包腳本
├── assets/          # 靜態資源
└── data/            # 執行時資料
```
