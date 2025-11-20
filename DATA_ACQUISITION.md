# Data Acquisition Guide

This document explains how to obtain all necessary data for the V-Recycler project, as data files are excluded from version control due to their size.

## Overview

The project requires two types of data:
1. **TrashNet Dataset** - Foreground objects for training
2. **Background Images** - Cluttered scenes for synthetic compositing

## Prerequisites

Ensure you have Python 3.8+ and have set up your virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell - if you get execution policy error, use the direct path method below)
.\venv\Scripts\Activate.ps1

# Alternative: Use Python directly without activation
.\venv\Scripts\python.exe

# Install dependencies
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 1. TrashNet Dataset

### Automatic Download (Recommended)

The TrashNet dataset (~2,500 images across 6 classes) can be automatically downloaded from Hugging Face:

```bash
.\venv\Scripts\python.exe scripts\download_trashnet.py
```

**What this does:**
- Downloads all TrashNet images from `garythung/trashnet` on Hugging Face
- Organizes images into class folders: `cardboard/`, `glass/`, `metal/`, `paper/`, `plastic/`, `trash/`
- Places everything in `data/raw/trashnet/`

**Expected output structure:**
```
data/raw/trashnet/
├── cardboard/     (~400 images)
├── glass/         (~500 images)
├── metal/         (~400 images)
├── paper/         (~600 images)
├── plastic/       (~500 images)
└── trash/         (~140 images)
```

### Manual Download (Alternative)

If the automatic download fails or you prefer manual setup:

1. Visit: https://huggingface.co/datasets/garythung/trashnet
2. Download the dataset
3. Extract to `data/raw/trashnet/` with the folder structure shown above

**Or** download from the original GitHub repository:
- https://github.com/garythung/trashnet

## 2. Background Images

Background images are **not included** and must be collected separately. You need images of cluttered trash scenes, bins, and recycling environments.

### Sources for Background Images

**Option A: Search and Download**
Search for and download images of:
- Trash piles and landfills
- Recycling bins (from various angles)
- Cluttered tables/floors with trash
- Mixed waste scenes
- Industrial waste areas

Keywords to search: "trash pile", "recycling bin", "waste sorting", "cluttered trash", "garbage collection"

**Option B: Use Public Datasets**
- **COCO Dataset**: Filter for images containing trash, bins, or cluttered scenes
- **OpenImages**: Search for relevant categories
- **Pixabay/Unsplash**: Free stock photos (check licenses)

**Option C: Capture Your Own**
- Take photos of your own trash/recycling bins
- Photograph cluttered areas with multiple objects
- Vary lighting conditions, angles, and backgrounds

### Background Requirements

- **Quantity**: At least 50-100 diverse images (more is better)
- **Resolution**: Minimum 640x640 pixels, preferably 1024x1024+
- **Variety**: Different lighting, angles, clutter levels, and settings
- **Format**: JPG or PNG

### Where to Place Backgrounds

```bash
data/raw/backgrounds/
├── bg_001.jpg
├── bg_002.jpg
├── bg_003.jpg
└── ...
```

**Important:** Background images should show cluttered, realistic scenes but should NOT already contain clearly visible recyclable items that would confuse the model.

## 3. Verify Data Setup

After downloading both datasets, verify the structure:

```bash
# Check TrashNet
.\venv\Scripts\python.exe -c "from pathlib import Path; print('TrashNet images:', len(list(Path('data/raw/trashnet').rglob('*.jpg'))))"

# Check backgrounds
.\venv\Scripts\python.exe -c "from pathlib import Path; print('Background images:', len(list(Path('data/raw/backgrounds').rglob('*.jpg'))) + len(list(Path('data/raw/backgrounds').rglob('*.png'))))"
```

Expected output:
- TrashNet: ~2,500 images
- Backgrounds: Your collected count (minimum 50)

## Data Size Expectations

| Dataset | Size | Image Count |
|---------|------|-------------|
| TrashNet Raw | ~100-150 MB | ~2,500 |
| Backgrounds | ~50-500 MB | 50-500 |
| Processed Foregrounds | ~150-200 MB | ~2,500 |
| Synthetic Dataset | ~500 MB - 5 GB | 1,000-10,000 |

## Next Steps

Once data is acquired:

1. **Extract Foregrounds**: See `DATA_SYNTHESIS_GUIDE.md` Step 1
2. **Generate Synthetic Scenes**: See `DATA_SYNTHESIS_GUIDE.md` Step 2
3. **Train Model**: See `planning_docs/03_yolov8_seg_training_plan.md`

## Troubleshooting

### TrashNet Download Issues

**Error: "Connection timeout" or "Download failed"**
- Check internet connection
- Try manual download from Hugging Face website
- Use a VPN if Hugging Face is blocked in your region

**Error: "Module 'datasets' not found"**
```bash
.\venv\Scripts\python.exe -m pip install datasets
```

### Background Images Issues

**"No background images found"**
- Ensure images are in `data/raw/backgrounds/`
- Check file extensions (`.jpg`, `.jpeg`, `.png`)
- Verify images are not in subdirectories

**"Background images too small"**
- Resize images to at least 640x640: 
```python
from PIL import Image
img = Image.open('small.jpg')
img = img.resize((1024, 1024))
img.save('resized.jpg')
```

## Data Usage Guidelines

- **License**: TrashNet is MIT licensed - cite original authors if publishing
- **Backgrounds**: Ensure you have rights to use collected images
- **Synthetic Data**: Generated data inherits licenses from source materials
- **Privacy**: Do not include personally identifiable information in backgrounds

## Citation

If using TrashNet, please cite:
```
@misc{trashnet,
  author = {Gary Thung, Mindy Yang},
  title = {TrashNet},
  year = {2016},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/garythung/trashnet}}
}
```

## Support

For issues with data acquisition:
1. Check this guide thoroughly
2. Review `DATA_SYNTHESIS_GUIDE.md`
3. Check planning documents in `planning_docs/`
4. Verify file paths and permissions
