"""
Extract foreground objects from TrashNet images using GrabCut segmentation.
Saves results as RGBA PNGs with alpha channel representing the object mask.
"""

import os
import cv2
import numpy as np
from PIL import Image
import json
import argparse
from pathlib import Path
from tqdm import tqdm


# Class mapping from TrashNet folder names to our target classes
CLASS_MAPPING = {
    'cardboard': 'paper_cardboard',
    'glass': 'glass',
    'metal': 'metal',
    'paper': 'paper_cardboard',
    'plastic': 'plastic',
    'trash': 'other_trash',
}


def extract_foreground_grabcut(image_path: str, iterations: int = 5) -> tuple[np.ndarray, np.ndarray]:
    """
    Extract foreground object using GrabCut algorithm.
    
    Args:
        image_path: Path to input image
        iterations: Number of GrabCut iterations
        
    Returns:
        Tuple of (rgba_image, mask) as numpy arrays
    """
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    # Create initial mask and background/foreground models
    mask = np.zeros(img.shape[:2], np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    
    # Define rectangle around object (assume object is centered with some margin)
    h, w = img.shape[:2]
    margin_x = int(w * 0.05)
    margin_y = int(h * 0.05)
    rect = (margin_x, margin_y, w - 2*margin_x, h - 2*margin_y)
    
    # Apply GrabCut
    cv2.grabCut(img, mask, rect, bgd_model, fgd_model, iterations, cv2.GC_INIT_WITH_RECT)
    
    # Create binary mask (0 for background, 1 for foreground)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    
    # Apply morphological operations to clean up mask
    kernel = np.ones((3, 3), np.uint8)
    mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask2 = cv2.morphologyEx(mask2, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Convert to RGBA
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    alpha = (mask2 * 255).astype(np.uint8)
    rgba = np.dstack((img_rgb, alpha))
    
    return rgba, mask2 * 255


def extract_foreground_simple_threshold(image_path: str, bg_color_threshold: int = 200) -> tuple[np.ndarray, np.ndarray]:
    """
    Extract foreground using simple background color thresholding.
    Works well for images with white/light backgrounds.
    
    Args:
        image_path: Path to input image
        bg_color_threshold: Threshold for background color (higher = lighter)
        
    Returns:
        Tuple of (rgba_image, mask) as numpy arrays
    """
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Create mask (dark areas are foreground)
    _, mask = cv2.threshold(gray, bg_color_threshold, 255, cv2.THRESH_BINARY_INV)
    
    # Apply morphological operations
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Convert to RGBA
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    rgba = np.dstack((img_rgb, mask))
    
    return rgba, mask


def process_trashnet_folder(
    input_folder: str,
    output_folder: str,
    method: str = 'grabcut',
    max_images_per_class: int | None = None,
) -> None:
    """
    Process all TrashNet images in a folder structure.
    
    Args:
        input_folder: Root folder containing TrashNet class subfolders
        output_folder: Output folder for processed foregrounds
        method: Extraction method ('grabcut' or 'threshold')
        max_images_per_class: Maximum number of images to process per class (None = all)
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create metadata file
    metadata = {
        'method': method,
        'images': []
    }
    
    total_processed = 0
    total_failed = 0
    
    # Process each class folder
    for class_folder in input_path.iterdir():
        if not class_folder.is_dir():
            continue
        
        class_name = class_folder.name.lower()
        if class_name not in CLASS_MAPPING:
            print(f"Skipping unknown class: {class_name}")
            continue
        
        target_class = CLASS_MAPPING[class_name]
        
        # Create output subfolder
        class_output_path = output_path / target_class
        class_output_path.mkdir(exist_ok=True)
        
        # Get image files
        image_files = list(class_folder.glob('*.jpg')) + list(class_folder.glob('*.png'))
        
        if max_images_per_class:
            image_files = image_files[:max_images_per_class]
        
        print(f"\nProcessing class: {class_name} -> {target_class} ({len(image_files)} images)")
        
        # Process each image
        for img_file in tqdm(image_files, desc=f"  {target_class}"):
            try:
                # Extract foreground
                if method == 'grabcut':
                    rgba, mask = extract_foreground_grabcut(str(img_file))
                elif method == 'threshold':
                    rgba, mask = extract_foreground_simple_threshold(str(img_file))
                else:
                    raise ValueError(f"Unknown method: {method}")
                
                # Save RGBA image
                output_filename = f"{img_file.stem}_fg.png"
                output_filepath = class_output_path / output_filename
                
                pil_image = Image.fromarray(rgba, 'RGBA')
                pil_image.save(output_filepath)
                
                # Add to metadata
                metadata['images'].append({
                    'filename': output_filename,
                    'class': target_class,
                    'source': str(img_file.relative_to(input_path)),
                    'width': rgba.shape[1],
                    'height': rgba.shape[0],
                })
                
                total_processed += 1
                
            except Exception as e:
                print(f"    Failed to process {img_file.name}: {e}")
                total_failed += 1
    
    # Save metadata
    metadata_path = output_path / 'metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"Total processed: {total_processed}")
    print(f"Total failed: {total_failed}")
    print(f"Output folder: {output_folder}")
    print(f"Metadata saved to: {metadata_path}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description='Extract foregrounds from TrashNet images')
    parser.add_argument(
        '--input',
        type=str,
        default='data/raw/trashnet',
        help='Input folder containing TrashNet class subfolders'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/processed/foregrounds',
        help='Output folder for processed foregrounds'
    )
    parser.add_argument(
        '--method',
        type=str,
        choices=['grabcut', 'threshold'],
        default='grabcut',
        help='Foreground extraction method'
    )
    parser.add_argument(
        '--max-per-class',
        type=int,
        default=None,
        help='Maximum number of images to process per class (default: all)'
    )
    
    args = parser.parse_args()
    
    process_trashnet_folder(
        args.input,
        args.output,
        method=args.method,
        max_images_per_class=args.max_per_class,
    )


if __name__ == '__main__':
    main()
