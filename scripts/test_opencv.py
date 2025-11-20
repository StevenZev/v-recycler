"""Quick test to verify OpenCV and image processing works"""
import cv2
import numpy as np
from pathlib import Path

print("Testing OpenCV installation...")

# Find first TrashNet image
trashnet_path = Path("data/raw/trashnet")
first_image = None

for class_folder in trashnet_path.iterdir():
    if class_folder.is_dir():
        images = list(class_folder.glob("*.jpg"))
        if images:
            first_image = images[0]
            break

if not first_image:
    print("ERROR: No TrashNet images found!")
    exit(1)

print(f"Testing with: {first_image}")

# Try to load and process
print("Loading image...")
img = cv2.imread(str(first_image))
if img is None:
    print("ERROR: Could not load image!")
    exit(1)

print(f"Image loaded: {img.shape}")
print("OpenCV is working!")
print("\nIf you see this, the issue is with the progress bar or GrabCut performance.")
print("Recommendation: Use --method threshold for faster processing")
