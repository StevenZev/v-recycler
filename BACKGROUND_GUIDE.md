# Background Images: Quick Collection Guide

You need 50-100 background images showing cluttered trash/recycling scenes. Here are the fastest ways to get them:

## 🎯 Quick Sources (15-30 minutes)

### Option 1: Pixabay (Free, No Attribution Required)
1. Go to https://pixabay.com/
2. Search terms:
   - "trash pile"
   - "garbage bin"
   - "recycling center"
   - "waste management"
   - "landfill"
   - "cluttered floor"
3. Download Medium or Large size (1280px+)
4. Save to `data/raw/backgrounds/`

### Option 2: Unsplash (Free, No Attribution Required)
1. Go to https://unsplash.com/
2. Search similar terms as above
3. Download Regular size (1920px+)
4. Save to `data/raw/backgrounds/`

### Option 3: Pexels (Free, No Attribution Required)
1. Go to https://www.pexels.com/
2. Search for trash/recycling scenes
3. Download Medium or Large size
4. Save to `data/raw/backgrounds/`

### Option 4: Your Phone Camera (Best for Real-World Performance!)
Take photos of:
- Your trash/recycling bins from various angles
- Cluttered kitchen counter with packaging
- Floor with scattered items
- Mixed waste in bags
- Parking lot with litter
- Public trash cans

**Tips:**
- Take 20-30 photos in different locations
- Vary the lighting (indoor, outdoor, evening)
- Include different clutter levels
- Use landscape orientation
- Aim for 1024x1024+ resolution

## 📋 What Makes a Good Background?

✅ **Good backgrounds:**
- Cluttered scenes with varied textures
- Multiple surfaces (floor, table, concrete)
- Different lighting conditions
- Various angles and perspectives
- Indoor and outdoor settings
- Empty or mostly empty backgrounds
- Natural clutter patterns

❌ **Avoid:**
- Backgrounds with clearly visible recyclables already in frame
- Too clean/minimalist (defeats the purpose)
- Heavy text or logos (may confuse model)
- People or faces (privacy concerns)
- Copyrighted artwork

## 🎨 Example Search Queries

Copy these into image search sites:
```
trash pile background
recycling bin empty
garbage container
waste sorting facility
cluttered floor texture
industrial waste
parking lot ground
concrete floor texture
kitchen counter clutter
office desk messy
warehouse floor
loading dock
alley background
dumpster area
waste collection
```

## 📏 Technical Requirements

- **Minimum resolution**: 640x640 pixels
- **Recommended**: 1024x1024 pixels or larger
- **Format**: JPG or PNG
- **Quantity**: Minimum 50, recommended 100-200
- **File naming**: Any name (e.g., bg_001.jpg, background1.png, trash_scene_42.jpg)

## 🚀 Quick Start Command

After collecting images and saving to `data/raw/backgrounds/`:

```bash
# Verify backgrounds were added
.\venv\Scripts\python.exe scripts\verify_setup.py

# If TrashNet and backgrounds are ready, extract foregrounds:
.\venv\Scripts\python.exe scripts\extract_foregrounds.py
```

## 💡 Pro Tips

1. **Diversity is key**: More variety in backgrounds = better generalization
2. **Start small**: Even 30 good backgrounds can work for initial testing
3. **Add incrementally**: You can always add more backgrounds and regenerate scenes
4. **Use real environments**: Photos from your target deployment environment work best
5. **Consider lighting**: Include shadows, bright spots, and various times of day

## 📦 Batch Download Tools

If you want to automate downloads:

```python
# Example: Download from Pixabay API (requires API key)
# See: https://pixabay.com/api/docs/

import requests
from pathlib import Path

API_KEY = "your_api_key_here"
keywords = ["trash+pile", "garbage+bin", "recycling"]
output = Path("data/raw/backgrounds")
output.mkdir(parents=True, exist_ok=True)

for keyword in keywords:
    url = f"https://pixabay.com/api/?key={API_KEY}&q={keyword}&per_page=20"
    response = requests.get(url)
    data = response.json()
    
    for i, hit in enumerate(data["hits"]):
        img_url = hit["largeImageURL"]
        img_data = requests.get(img_url).content
        filename = output / f"{keyword}_{i:03d}.jpg"
        filename.write_bytes(img_data)
        print(f"Downloaded: {filename}")
```

## ⏱️ Time Estimate

- Manual download: 15-30 minutes for 50 images
- Phone photos: 10-15 minutes for 30 images
- Automated script: 5-10 minutes for 100 images (requires setup)

---

**Need help?** See `DATA_ACQUISITION.md` for more detailed information.
