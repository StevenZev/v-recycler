# Data Synthesis Pipeline - Getting Started

This guide covers the data synthesis step for creating a YOLOv8 instance segmentation dataset for recyclable materials.

## Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download the TrashNet dataset:

**Option A: Automatic download from Hugging Face (recommended)**
```bash
python scripts/download_trashnet.py
```

**Option B: Manual download**
Download from [Hugging Face](https://huggingface.co/datasets/garythung/trashnet) or [GitHub](https://github.com/garythung/trashnet) and extract to `data/raw/trashnet/`

3. Collect background images (trash piles, bins, cluttered scenes) and place them in `data/raw/backgrounds/`

## Directory Structure

```
v-recycler/
├── data/
│   ├── raw/
│   │   ├── trashnet/          # TrashNet dataset (organized by class)
│   │   │   ├── cardboard/
│   │   │   ├── glass/
│   │   │   ├── metal/
│   │   │   ├── paper/
│   │   │   ├── plastic/
│   │   │   └── trash/
│   │   └── backgrounds/        # Background images (add your own)
│   ├── processed/
│   │   └── foregrounds/        # Extracted RGBA foregrounds (auto-generated)
│   └── synthetic/
│       ├── images/             # Generated synthetic scenes (auto-generated)
│       └── labels/             # YOLOv8 format labels (auto-generated)
├── scripts/
│   ├── extract_foregrounds.py
│   ├── generate_synthetic_scenes.py
│   └── utils.py
├── config/
│   └── dataset.yaml
└── planning_docs/
```

## Step 1: Extract Foregrounds from TrashNet

Process TrashNet images to extract foreground objects with alpha masks:

```bash
python scripts/extract_foregrounds.py --input data/raw/trashnet --output data/processed/foregrounds --method grabcut
```

**Options:**
- `--method`: Choose `grabcut` (default) or `threshold`
- `--max-per-class`: Limit number of images per class (e.g., 100 for testing)

**Output:**
- RGBA PNG files in `data/processed/foregrounds/<class>/`
- `metadata.json` with image information

**Expected Classes:**
- `plastic` (from TrashNet 'plastic')
- `metal` (from TrashNet 'metal')
- `glass` (from TrashNet 'glass')
- `paper_cardboard` (from TrashNet 'cardboard' + 'paper')
- `other_trash` (from TrashNet 'trash')

## Step 2: Generate Synthetic Training Scenes

Composite foreground objects onto background images:

```bash
python scripts/generate_synthetic_scenes.py --foregrounds data/processed/foregrounds --backgrounds data/raw/backgrounds --output-images data/synthetic/images --output-labels data/synthetic/labels --num-scenes 1000
```

**Options:**
- `--num-scenes`: Number of synthetic scenes to generate (default: 1000)
- `--min-objects`: Minimum objects per scene (default: 3)
- `--max-objects`: Maximum objects per scene (default: 8)
- `--scale-min`: Minimum scale factor (default: 0.3)
- `--scale-max`: Maximum scale factor (default: 1.0)
- `--rotation-min`: Minimum rotation degrees (default: -30)
- `--rotation-max`: Maximum rotation degrees (default: 30)
- `--flip-prob`: Horizontal flip probability (default: 0.5)

**Output:**
- Synthetic images in `data/synthetic/images/scene_XXXXXX.jpg`
- YOLOv8 segmentation labels in `data/synthetic/labels/scene_XXXXXX.txt`

## Label Format (YOLOv8 Segmentation)

Each label file contains one line per object:
```
<class_id> <x1> <y1> <x2> <y2> ... <xn> <yn>
```

Where:
- `class_id`: Integer class ID (0-4)
- `<x y>`: Normalized polygon coordinates (0.0-1.0)

## Next Steps

After generating synthetic data:

1. **Split dataset** into train/val/test sets
2. **Train YOLOv8-seg** model using `config/dataset.yaml`
3. **Evaluate** on synthetic test set
4. **Collect real images** and fine-tune
5. **Iterate** based on performance

See `planning_docs/03_yolov8_seg_training_plan.md` for training details.

## Troubleshooting

### No background images found
Add background images to `data/raw/backgrounds/`. You can:
- Download trash/recycling images from the internet
- Use images from datasets like COCO (filtering for relevant scenes)
- Take your own photos

### Foreground extraction quality
- Try different methods (`--method grabcut` vs `--method threshold`)
- Adjust background detection in the code if needed
- Manually review extracted foregrounds in `data/processed/foregrounds/`

### Too much/little overlap
- Adjust `is_overlap()` threshold in `scripts/utils.py`
- Modify `safe_paste_position()` parameters

## Tips for Better Results

1. **Diverse backgrounds**: Use varied lighting, textures, and angles
2. **Quality foregrounds**: Review extracted objects and remove poor masks
3. **Balanced classes**: Ensure each class has sufficient examples
4. **Realistic compositions**: Adjust scale/rotation ranges to match real scenarios
5. **Augmentation**: Consider additional augmentations during training

## Example Commands

Download TrashNet dataset:
```bash
python scripts/download_trashnet.py
```

Quick test with limited data:
```bash
# Extract 50 foregrounds per class
python scripts/extract_foregrounds.py --max-per-class 50

# Generate 100 test scenes
python scripts/generate_synthetic_scenes.py --num-scenes 100
```

Full dataset generation:
```bash
# Extract all foregrounds
python scripts/extract_foregrounds.py

# Generate 5000 training scenes
python scripts/generate_synthetic_scenes.py --num-scenes 5000 --min-objects 5 --max-objects 12
```
