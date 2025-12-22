# LabelStudio Skills

此目錄包含可供 AI Agents 調用的 Python 腳本。

## 概述

Skills 是一組封裝好的 Python 類別，提供標準化的介面讓 AI Agents 能夠：
- 查詢可用的操作 (通過 `get_info()` 方法)
- 執行資料庫操作
- 處理圖片和標註
- 匯出資料集

## 可用的 Skills

### DatasetSkill
資料集管理操作：
- `split_dataset()` - 分割資料集為 train/val/test
- `get_statistics()` - 取得資料集統計
- `list_images()` - 列出專案中的圖片

### AnnotationSkill
標註相關操作：
- `create_annotation()` - 建立標註
- `batch_create()` - 批次建立標註
- `get_annotations()` - 取得圖片的標註
- `validate_annotations()` - 驗證標註正確性

### ExportSkill
資料匯出操作：
- `export_dataset()` - 匯出資料集
- `get_export_formats()` - 取得支援的格式
- `preview_export()` - 預覽匯出內容

### AugmentationSkill
資料增強操作：
- `get_presets()` - 取得預設增強組合
- `get_options()` - 取得所有增強選項
- `preview_augmentation()` - 預覽增強效果
- `estimate_output()` - 估算增強後的資料量

## 使用方式

### 直接調用

```python
from skills import DatasetSkill

skill = DatasetSkill()

# 取得 skill 資訊
info = skill.get_info()
print(info)

# 分割資料集
result = skill.split_dataset(
    project_id=1,
    train=0.7,
    val=0.2,
    test=0.1,
    strategy='random'
)
print(result)
```

### Agent 調用模式

```python
# Agent 發現可用的 skills
from skills import DatasetSkill, ExportSkill

skills = [DatasetSkill(), ExportSkill()]

for skill in skills:
    info = skill.get_info()
    print(f"Skill: {info['name']}")
    print(f"Description: {info['description']}")
    for method, details in info['methods'].items():
        print(f"  - {method}: {details['description']}")
```

## 新增 Skill

1. 在 `skills/` 目錄下建立新的 Python 檔案
2. 繼承 `BaseSkill` 類別
3. 實作 `get_info()` 方法
4. 在 `skills/__init__.py` 中註冊

```python
from .base import BaseSkill

class MyCustomSkill(BaseSkill):
    def get_info(self):
        return {
            'name': 'MyCustomSkill',
            'description': 'My custom operations',
            'methods': {
                'my_method': {
                    'description': 'Does something useful',
                    'params': {
                        'param1': 'str - Description'
                    }
                }
            }
        }

    def my_method(self, param1: str):
        def _do_work():
            # 在 Flask context 中執行
            pass
        return self.execute_in_context(_do_work)
```
