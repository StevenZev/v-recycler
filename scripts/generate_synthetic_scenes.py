"""
Generate synthetic training scenes by compositing foreground objects onto backgrounds.
Creates YOLOv8 segmentation format labels for each generated image.
"""

import os
import random
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np
from PIL import Image
from tqdm import tqdm

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent))
from utils import (
    mask_to_polygon,
    yolo_bbox_from_mask,
    apply_transform_to_image,
    paste_with_alpha,
    safe_paste_position,
    create_composite_mask,
)


# Target classes (must match training config)
CLASSES = ['plastic', 'metal', 'glass', 'paper_cardboard', 'other_trash']
CLASS_TO_ID = {cls: idx for idx, cls in enumerate(CLASSES)}


class ForegroundDatabase:
    """Database of foreground objects organized by class."""
    
    def __init__(self, foreground_folder: str, metadata_path: str = None):
        """
        Initialize foreground database.
        
        Args:
            foreground_folder: Path to processed foregrounds folder
            metadata_path: Optional path to metadata.json
        """
        self.foreground_folder = Path(foreground_folder)
        self.foregrounds = {cls: [] for cls in CLASSES}
        
        # Load metadata if available
        if metadata_path is None:
            metadata_path = self.foreground_folder / 'metadata.json'
        
        if Path(metadata_path).exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                for item in metadata['images']:
                    class_name = item['class']
                    if class_name in self.foregrounds:
                        self.foregrounds[class_name].append(item)
        else:
            # Scan folders manually
            for class_name in CLASSES:
                class_folder = self.foreground_folder / class_name
                if class_folder.exists():
                    for img_path in class_folder.glob('*.png'):
                        self.foregrounds[class_name].append({
                            'filename': img_path.name,
                            'class': class_name,
                            'path': str(img_path),
                        })
        
        # Print statistics
        print("Foreground database loaded:")
        for class_name, items in self.foregrounds.items():
            print(f"  {class_name}: {len(items)} images")
    
    def get_random_foreground(self, class_name: str = None) -> Dict:
        """
        Get a random foreground object.
        
        Args:
            class_name: Optional class to sample from (None = any class)
            
        Returns:
            Dictionary with foreground metadata
        """
        if class_name is None:
            # Sample from all classes
            all_foregrounds = [fg for fgs in self.foregrounds.values() for fg in fgs]
            return random.choice(all_foregrounds)
        else:
            return random.choice(self.foregrounds[class_name])
    
    def load_foreground_image(self, foreground_info: Dict) -> Image.Image:
        """
        Load a foreground RGBA image.
        
        Args:
            foreground_info: Foreground metadata dictionary
            
        Returns:
            PIL Image in RGBA mode
        """
        if 'path' in foreground_info:
            path = foreground_info['path']
        else:
            class_name = foreground_info['class']
            filename = foreground_info['filename']
            path = self.foreground_folder / class_name / filename
        
        return Image.open(path).convert('RGBA')


class BackgroundDatabase:
    """Database of background images."""
    
    def __init__(self, background_folder: str):
        """
        Initialize background database.
        
        Args:
            background_folder: Path to backgrounds folder
        """
        self.background_folder = Path(background_folder)
        self.backgrounds = []
        
        # Scan for background images
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            self.backgrounds.extend(list(self.background_folder.glob(ext)))
        
        print(f"Background database loaded: {len(self.backgrounds)} images")
    
    def get_random_background(self) -> Image.Image:
        """
        Get a random background image.
        
        Returns:
            PIL Image in RGB mode
        """
        bg_path = random.choice(self.backgrounds)
        return Image.open(bg_path).convert('RGB')


def generate_synthetic_scene(
    bg_database: BackgroundDatabase,
    fg_database: ForegroundDatabase,
    num_objects: Tuple[int, int] = (3, 8),
    scale_range: Tuple[float, float] = (0.3, 1.0),
    rotation_range: Tuple[float, float] = (-30, 30),
    flip_prob: float = 0.5,
) -> Tuple[Image.Image, List[Dict]]:
    """
    Generate a single synthetic scene with annotations.
    
    Args:
        bg_database: Background database
        fg_database: Foreground database
        num_objects: Min and max number of objects to place
        scale_range: Min and max scale factors
        rotation_range: Min and max rotation angles
        flip_prob: Probability of horizontal flip
        
    Returns:
        Tuple of (composite_image, annotations_list)
    """
    # Get random background
    background = bg_database.get_random_background()
    bg_width, bg_height = background.size
    
    # Determine number of objects
    n_objects = random.randint(*num_objects)
    
    # Track existing bounding boxes to avoid excessive overlap
    existing_bboxes = []
    annotations = []
    
    # Composite image
    composite = background.copy()
    
    for _ in range(n_objects):
        # Get random foreground
        fg_info = fg_database.get_random_foreground()
        fg_image = fg_database.load_foreground_image(fg_info)
        
        # Apply random transformations
        scale = random.uniform(*scale_range)
        rotation = random.uniform(*rotation_range)
        flip = random.random() < flip_prob
        
        fg_transformed = apply_transform_to_image(fg_image, scale, rotation, flip)
        
        # Find safe position
        position = safe_paste_position(
            bg_width, bg_height,
            fg_transformed.width, fg_transformed.height,
            existing_bboxes,
            max_attempts=50
        )
        
        if position is None:
            # Skip if can't find valid position
            continue
        
        # Paste foreground onto background
        composite = paste_with_alpha(composite, fg_transformed, position)
        
        # Extract mask from alpha channel
        fg_array = np.array(fg_transformed)
        mask = fg_array[:, :, 3]  # Alpha channel
        
        # Create full-size mask at pasted position
        full_mask = create_composite_mask(bg_width, bg_height, mask, position)
        
        # Generate polygon coordinates
        polygon = mask_to_polygon(full_mask)
        
        if not polygon:
            # Skip if polygon generation failed
            continue
        
        # Get bounding box
        bbox = yolo_bbox_from_mask(full_mask)
        
        # Update existing bboxes (for overlap detection)
        x_center, y_center, width, height = bbox
        x_min = int((x_center - width/2) * bg_width)
        y_min = int((y_center - height/2) * bg_height)
        x_max = int((x_center + width/2) * bg_width)
        y_max = int((y_center + height/2) * bg_height)
        existing_bboxes.append((x_min, y_min, x_max, y_max))
        
        # Create annotation
        class_id = CLASS_TO_ID[fg_info['class']]
        annotations.append({
            'class_id': class_id,
            'class_name': fg_info['class'],
            'bbox': bbox,
            'polygon': polygon,
        })
    
    return composite, annotations


def save_yolo_annotation(annotations: List[Dict], output_path: str) -> None:
    """
    Save annotations in YOLOv8 segmentation format.
    
    Format: <class_id> <x1> <y1> <x2> <y2> ... <xn> <yn>
    
    Args:
        annotations: List of annotation dictionaries
        output_path: Path to save annotation file
    """
    with open(output_path, 'w') as f:
        for ann in annotations:
            class_id = ann['class_id']
            polygon = ann['polygon']
            
            # Write line: class_id followed by polygon coordinates
            line = f"{class_id}"
            for coord in polygon:
                line += f" {coord:.6f}"
            f.write(line + '\n')


def generate_dataset(
    bg_database: BackgroundDatabase,
    fg_database: ForegroundDatabase,
    output_images_folder: str,
    output_labels_folder: str,
    num_scenes: int,
    num_objects: Tuple[int, int] = (3, 8),
    scale_range: Tuple[float, float] = (0.3, 1.0),
    rotation_range: Tuple[float, float] = (-30, 30),
    flip_prob: float = 0.5,
) -> None:
    """
    Generate a complete synthetic dataset.
    
    Args:
        bg_database: Background database
        fg_database: Foreground database
        output_images_folder: Output folder for images
        output_labels_folder: Output folder for labels
        num_scenes: Number of scenes to generate
        num_objects: Min and max objects per scene
        scale_range: Scale factor range
        rotation_range: Rotation angle range in degrees
        flip_prob: Horizontal flip probability
    """
    images_path = Path(output_images_folder)
    labels_path = Path(output_labels_folder)
    images_path.mkdir(parents=True, exist_ok=True)
    labels_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\nGenerating {num_scenes} synthetic scenes...")
    print(f"Objects per scene: {num_objects[0]}-{num_objects[1]}")
    print(f"Scale range: {scale_range}")
    print(f"Rotation range: {rotation_range}")
    print(f"Flip probability: {flip_prob}")
    print()
    
    successful = 0
    empty = 0
    
    for i in tqdm(range(num_scenes), desc="Generating scenes"):
        try:
            # Generate scene
            composite, annotations = generate_synthetic_scene(
                bg_database, fg_database,
                num_objects=num_objects,
                scale_range=scale_range,
                rotation_range=rotation_range,
                flip_prob=flip_prob,
            )
            
            if not annotations:
                empty += 1
                continue
            
            # Save image
            image_filename = f"scene_{i:06d}.jpg"
            image_path = images_path / image_filename
            composite.save(image_path, quality=95)
            
            # Save annotation
            label_filename = f"scene_{i:06d}.txt"
            label_path = labels_path / label_filename
            save_yolo_annotation(annotations, label_path)
            
            successful += 1
            
        except Exception as e:
            print(f"\nError generating scene {i}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Dataset generation complete!")
    print(f"Successful: {successful}")
    print(f"Empty (skipped): {empty}")
    print(f"Images saved to: {output_images_folder}")
    print(f"Labels saved to: {output_labels_folder}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic training scenes')
    parser.add_argument(
        '--foregrounds',
        type=str,
        default='data/processed/foregrounds',
        help='Path to processed foregrounds folder'
    )
    parser.add_argument(
        '--backgrounds',
        type=str,
        default='data/raw/backgrounds',
        help='Path to backgrounds folder'
    )
    parser.add_argument(
        '--output-images',
        type=str,
        default='data/synthetic/images',
        help='Output folder for generated images'
    )
    parser.add_argument(
        '--output-labels',
        type=str,
        default='data/synthetic/labels',
        help='Output folder for annotation labels'
    )
    parser.add_argument(
        '--num-scenes',
        type=int,
        default=1000,
        help='Number of synthetic scenes to generate'
    )
    parser.add_argument(
        '--min-objects',
        type=int,
        default=3,
        help='Minimum number of objects per scene'
    )
    parser.add_argument(
        '--max-objects',
        type=int,
        default=8,
        help='Maximum number of objects per scene'
    )
    parser.add_argument(
        '--scale-min',
        type=float,
        default=0.3,
        help='Minimum scale factor'
    )
    parser.add_argument(
        '--scale-max',
        type=float,
        default=1.0,
        help='Maximum scale factor'
    )
    parser.add_argument(
        '--rotation-min',
        type=float,
        default=-30,
        help='Minimum rotation angle (degrees)'
    )
    parser.add_argument(
        '--rotation-max',
        type=float,
        default=30,
        help='Maximum rotation angle (degrees)'
    )
    parser.add_argument(
        '--flip-prob',
        type=float,
        default=0.5,
        help='Horizontal flip probability'
    )
    
    args = parser.parse_args()
    
    # Load databases
    fg_database = ForegroundDatabase(args.foregrounds)
    bg_database = BackgroundDatabase(args.backgrounds)
    
    if not bg_database.backgrounds:
        print("ERROR: No background images found!")
        print(f"Please add images to: {args.backgrounds}")
        return
    
    # Generate dataset
    generate_dataset(
        bg_database,
        fg_database,
        args.output_images,
        args.output_labels,
        args.num_scenes,
        num_objects=(args.min_objects, args.max_objects),
        scale_range=(args.scale_min, args.scale_max),
        rotation_range=(args.rotation_min, args.rotation_max),
        flip_prob=args.flip_prob,
    )


if __name__ == '__main__':
    main()
