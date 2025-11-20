# V-Recycler: Quick Start Guide

End-to-end guide for setting up and running the recyclable materials instance segmentation project.

## 🚀 Quick Setup (5 minutes)

```bash
# 1. Clone and navigate to project
cd v-recycler

# 2. Create virtual environment
python -m venv venv

# 3. Install dependencies (use direct path to avoid PowerShell execution policy issues)
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# 4. Download TrashNet dataset (~2,500 images)
.\venv\Scripts\python.exe scripts\download_trashnet.py

# 5. Add background images to data/raw/backgrounds/
#    (See DATA_ACQUISITION.md for sources)
```

## 📋 Project Overview

**Goal**: Train a YOLOv8 instance segmentation model to detect and classify recyclable materials in cluttered scenes.

**Classes**: 
- Plastic
- Metal  
- Glass
- Paper/Cardboard
- Other Trash

**Approach**: Synthetic data generation → Train YOLOv8 → Fine-tune on real images

## 📁 Project Structure

```
v-recycler/
├── data/                          # Data files (gitignored)
│   ├── raw/
│   │   ├── trashnet/             # Downloaded TrashNet images
│   │   └── backgrounds/          # Your background images
│   ├── processed/
│   │   └── foregrounds/          # Extracted RGBA objects
│   └── synthetic/
│       ├── images/               # Generated training images
│       └── labels/               # YOLOv8 format labels
├── scripts/
│   ├── download_trashnet.py      # Download TrashNet from HF
│   ├── extract_foregrounds.py    # Extract objects with masks
│   ├── generate_synthetic_scenes.py  # Create training data
│   └── utils.py                  # Helper functions
├── config/
│   └── dataset.yaml              # YOLOv8 dataset config
├── planning_docs/                # Detailed specifications
│   ├── 01_project_overview.md
│   ├── 02_data_generation_spec.md
│   ├── 03_yolov8_seg_training_plan.md
│   └── 04_evaluation_and_iteration_plan.md
├── DATA_ACQUISITION.md           # How to get data
├── DATA_SYNTHESIS_GUIDE.md       # Detailed usage guide
└── requirements.txt              # Python dependencies
```

## 🔄 Complete Workflow

### Phase 1: Data Acquisition ⬇️

See `DATA_ACQUISITION.md` for detailed instructions.

```bash
# Download TrashNet automatically
.\venv\Scripts\python.exe scripts\download_trashnet.py

# Collect 50-100 background images and place in:
# data/raw/backgrounds/
```

### Phase 2: Foreground Extraction 🎭

Extract recyclable objects from TrashNet with alpha masks:

```bash
# Full extraction (all ~2,500 images)
.\venv\Scripts\python.exe scripts\extract_foregrounds.py

# Or test with limited images first
.\venv\Scripts\python.exe scripts\extract_foregrounds.py --max-per-class 50
```

**Output**: RGBA PNG files in `data/processed/foregrounds/<class>/`

### Phase 3: Synthetic Data Generation 🎨

Composite foregrounds onto backgrounds to create training data:

```bash
# Generate 1,000 training scenes (good starting point)
.\venv\Scripts\python.exe scripts\generate_synthetic_scenes.py --num-scenes 1000

# Or generate larger dataset for better performance
.\venv\Scripts\python.exe scripts\generate_synthetic_scenes.py --num-scenes 5000 --min-objects 5 --max-objects 12
```

**Output**: 
- Images: `data/synthetic/images/scene_XXXXXX.jpg`
- Labels: `data/synthetic/labels/scene_XXXXXX.txt` (YOLOv8 format)

### Phase 4: Training 🏋️

```bash
# Install Ultralytics YOLOv8
.\venv\Scripts\python.exe -m pip install ultralytics

# Train YOLOv8-seg model
.\venv\Scripts\python.exe -m ultralytics train \
    model=yolov8n-seg.pt \
    data=config/dataset.yaml \
    epochs=100 \
    imgsz=640 \
    batch=16
```

See `planning_docs/03_yolov8_seg_training_plan.md` for detailed training instructions.

### Phase 5: Evaluation & Iteration 📊

See `planning_docs/04_evaluation_and_iteration_plan.md` for:
- Performance metrics
- Test set evaluation
- Real-world validation
- Fine-tuning strategies

## 🎛️ Configuration Options

### Foreground Extraction

```bash
.\venv\Scripts\python.exe scripts\extract_foregrounds.py \
    --input data/raw/trashnet \
    --output data/processed/foregrounds \
    --method grabcut \              # or 'threshold'
    --max-per-class 100             # limit for testing
```

### Synthetic Generation

```bash
.\venv\Scripts\python.exe scripts\generate_synthetic_scenes.py \
    --num-scenes 1000 \             # number of images
    --min-objects 3 \               # min objects per scene
    --max-objects 8 \               # max objects per scene
    --scale-min 0.3 \               # min scale factor
    --scale-max 1.0 \               # max scale factor
    --rotation-min -30 \            # rotation range
    --rotation-max 30 \
    --flip-prob 0.5                 # horizontal flip chance
```

## 📊 Expected Results

| Dataset Size | Training Time | Expected mAP@0.5 |
|--------------|---------------|------------------|
| 1,000 scenes | ~1-2 hours    | 0.50-0.60        |
| 5,000 scenes | ~3-5 hours    | 0.60-0.70        |
| 10,000 scenes | ~6-10 hours  | 0.65-0.75        |

*Estimates based on YOLOv8n-seg on a modern GPU*

## 🐛 Common Issues

### "No backgrounds found"
Add at least 50 images to `data/raw/backgrounds/`

### "PowerShell execution policy error"
Use direct Python path: `.\venv\Scripts\python.exe` instead of activating

### "CUDA out of memory"
Reduce batch size in training: `batch=8` or `batch=4`

### "Poor mask quality"
Try different extraction method: `--method threshold` instead of `grabcut`

## 📚 Documentation

- **DATA_ACQUISITION.md** - How to obtain all required data
- **DATA_SYNTHESIS_GUIDE.md** - Detailed data generation guide
- **planning_docs/** - Complete project specifications and plans

## 🔧 Development Tips

1. **Start small**: Test with `--max-per-class 50` and `--num-scenes 100`
2. **Check outputs**: Review generated images in `data/synthetic/images/`
3. **Iterate**: Adjust augmentation parameters based on visual inspection
4. **Monitor training**: Use TensorBoard to track metrics
5. **Save checkpoints**: YOLOv8 auto-saves to `runs/segment/train/`

## 🎯 Next Steps After Training

1. Evaluate model on synthetic test set
2. Test on real photos of recyclables
3. Collect and annotate real-world images
4. Fine-tune model with real data
5. Deploy to production (edge device, cloud API, etc.)

## 📖 Additional Resources

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [TrashNet Dataset](https://huggingface.co/datasets/garythung/trashnet)
- Project planning docs in `planning_docs/`

---

**Ready to start?** Begin with Phase 1 (Data Acquisition) and follow the workflow sequentially!
