# Project Overview: Recyclable Materials Instance Segmentation (YOLOv8-seg)

## 1. Goal

Build an instance segmentation model using YOLOv8-seg that can:
- Detect and segment individual recyclable items in cluttered trash scenes.
- Classify each instance into recycling-relevant categories (e.g., plastic, metal, glass, paper/cardboard, non-recyclable).

The model will be trained primarily on synthetic data created by compositing foreground TrashNet objects onto cluttered background images, with later fine-tuning on real-world images.

---

## 2. High-Level Approach

1. **Foreground Extraction**
   - Use TrashNet images as single-object foregrounds.
   - Derive per-pixel masks for each object (via classical segmentation or a pretrained model).
   - Save results as RGBA PNGs (alpha channel encodes the object mask).

2. **Background Collection**
   - Gather diverse images of trash piles, bins, ground, and cluttered scenes.
   - These serve as backgrounds on which foreground objects are pasted.

3. **Synthetic Scene Generation**
   - Randomly sample background images.
   - Randomly choose and transform multiple foreground objects (scale, rotation, placement).
   - Composite them into new images.
   - Record YOLOv8-seg labels for each instance (class id, bounding box, segmentation polygon).

4. **Dataset Preparation for YOLOv8-seg**
   - Organize images and labels in the YOLO directory structure.
   - Create segmentation label files in YOLOv8 format.
   - Create dataset config YAML file for Ultralytics.

5. **Training and Evaluation**
   - Train YOLOv8-seg from COCO-pretrained weights on the synthetic dataset.
   - Evaluate on a held-out synthetic test set and on real photos.
   - Collect real-world images, annotate them (possibly using model-assisted labeling), and fine-tune.

---

## 3. Target Classes

1. `plastic`
2. `metal`
3. `glass`
4. `paper_cardboard`
5. `other_trash`

---

## 4. Planned Tech Stack

Python, Pillow, OpenCV, NumPy, Ultralytics YOLOv8.

---

## 5. Repository Structure (Proposed)

(Structure omitted for brevity here; identical to prior message.)

---

## 6. Milestones

Foreground extraction → Synthetic generation → YOLO training → Real data fine-tuning → Evaluation.
