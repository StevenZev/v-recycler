"""
Utility functions for data synthesis pipeline.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List
import random


def mask_to_polygon(mask: np.ndarray, epsilon_factor: float = 0.005) -> List[List[float]]:
    """
    Convert a binary mask to a polygon in YOLOv8 segmentation format.
    
    Args:
        mask: Binary mask (H, W) with values 0 or 255
        epsilon_factor: Approximation accuracy factor for contour simplification
        
    Returns:
        List of normalized [x, y] coordinates forming the polygon
    """
    # Find contours
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return []
    
    # Get the largest contour
    contour = max(contours, key=cv2.contourArea)
    
    # Simplify contour
    epsilon = epsilon_factor * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    
    # Convert to normalized coordinates
    h, w = mask.shape
    polygon = []
    for point in approx:
        x, y = point[0]
        polygon.extend([x / w, y / h])
    
    return polygon


def bbox_from_mask(mask: np.ndarray) -> Tuple[int, int, int, int]:
    """
    Get bounding box from binary mask.
    
    Args:
        mask: Binary mask (H, W)
        
    Returns:
        Tuple of (x_min, y_min, x_max, y_max)
    """
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    
    if not rows.any() or not cols.any():
        return (0, 0, 0, 0)
    
    y_min, y_max = np.where(rows)[0][[0, -1]]
    x_min, x_max = np.where(cols)[0][[0, -1]]
    
    return (int(x_min), int(y_min), int(x_max), int(y_max))


def yolo_bbox_from_mask(mask: np.ndarray) -> Tuple[float, float, float, float]:
    """
    Get YOLOv8 normalized bounding box from mask.
    
    Args:
        mask: Binary mask (H, W)
        
    Returns:
        Tuple of (x_center, y_center, width, height) normalized to [0, 1]
    """
    x_min, y_min, x_max, y_max = bbox_from_mask(mask)
    h, w = mask.shape
    
    if x_max == 0 and y_max == 0:
        return (0.0, 0.0, 0.0, 0.0)
    
    x_center = ((x_min + x_max) / 2) / w
    y_center = ((y_min + y_max) / 2) / h
    width = (x_max - x_min) / w
    height = (y_max - y_min) / h
    
    return (x_center, y_center, width, height)


def random_transform_params(
    scale_range: Tuple[float, float] = (0.3, 1.0),
    rotation_range: Tuple[float, float] = (-30, 30),
) -> dict:
    """
    Generate random transformation parameters.
    
    Args:
        scale_range: Min and max scale factors
        rotation_range: Min and max rotation angles in degrees
        
    Returns:
        Dictionary with 'scale' and 'rotation' keys
    """
    return {
        'scale': random.uniform(*scale_range),
        'rotation': random.uniform(*rotation_range),
    }


def apply_transform_to_image(
    image: Image.Image,
    scale: float,
    rotation: float,
    flip_horizontal: bool = False,
) -> Image.Image:
    """
    Apply transformations to an image (RGBA).
    
    Args:
        image: PIL Image in RGBA mode
        scale: Scale factor
        rotation: Rotation angle in degrees
        flip_horizontal: Whether to flip horizontally
        
    Returns:
        Transformed PIL Image
    """
    # Scale
    new_size = (int(image.width * scale), int(image.height * scale))
    image = image.resize(new_size, Image.Resampling.LANCZOS)
    
    # Rotate
    image = image.rotate(rotation, expand=True, resample=Image.Resampling.BICUBIC)
    
    # Flip
    if flip_horizontal:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
    
    return image


def paste_with_alpha(
    background: Image.Image,
    foreground: Image.Image,
    position: Tuple[int, int],
) -> Image.Image:
    """
    Paste foreground onto background using alpha channel.
    
    Args:
        background: PIL Image (RGB mode)
        foreground: PIL Image (RGBA mode)
        position: (x, y) position for top-left corner of foreground
        
    Returns:
        Composite PIL Image (RGB mode)
    """
    # Create a copy of background
    result = background.copy()
    
    # Paste using alpha channel as mask
    result.paste(foreground, position, foreground)
    
    return result


def is_overlap(bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int], threshold: float = 0.3) -> bool:
    """
    Check if two bounding boxes overlap significantly.
    
    Args:
        bbox1: (x_min, y_min, x_max, y_max)
        bbox2: (x_min, y_min, x_max, y_max)
        threshold: IoU threshold for considering overlap
        
    Returns:
        True if overlap exceeds threshold
    """
    x1_min, y1_min, x1_max, y1_max = bbox1
    x2_min, y2_min, x2_max, y2_max = bbox2
    
    # Calculate intersection
    x_inter_min = max(x1_min, x2_min)
    y_inter_min = max(y1_min, y2_min)
    x_inter_max = min(x1_max, x2_max)
    y_inter_max = min(y1_max, y2_max)
    
    if x_inter_max < x_inter_min or y_inter_max < y_inter_min:
        return False
    
    inter_area = (x_inter_max - x_inter_min) * (y_inter_max - y_inter_min)
    
    # Calculate union
    area1 = (x1_max - x1_min) * (y1_max - y1_min)
    area2 = (x2_max - x2_min) * (y2_max - y2_min)
    union_area = area1 + area2 - inter_area
    
    # Calculate IoU
    iou = inter_area / union_area if union_area > 0 else 0
    
    return iou > threshold


def safe_paste_position(
    bg_width: int,
    bg_height: int,
    fg_width: int,
    fg_height: int,
    existing_bboxes: List[Tuple[int, int, int, int]],
    max_attempts: int = 50,
) -> Tuple[int, int] | None:
    """
    Find a safe position to paste foreground without significant overlap.
    
    Args:
        bg_width: Background width
        bg_height: Background height
        fg_width: Foreground width
        fg_height: Foreground height
        existing_bboxes: List of existing object bounding boxes
        max_attempts: Maximum number of random attempts
        
    Returns:
        (x, y) position or None if no valid position found
    """
    for _ in range(max_attempts):
        x = random.randint(0, max(0, bg_width - fg_width))
        y = random.randint(0, max(0, bg_height - fg_height))
        
        new_bbox = (x, y, x + fg_width, y + fg_height)
        
        # Check overlap with existing boxes
        has_overlap = any(is_overlap(new_bbox, bbox) for bbox in existing_bboxes)
        
        if not has_overlap:
            return (x, y)
    
    return None


def create_composite_mask(
    bg_width: int,
    bg_height: int,
    fg_mask: np.ndarray,
    position: Tuple[int, int],
) -> np.ndarray:
    """
    Create a full-size mask for a foreground object at given position.
    
    Args:
        bg_width: Background width
        bg_height: Background height
        fg_mask: Foreground mask (H, W)
        position: (x, y) top-left position
        
    Returns:
        Full-size mask (bg_height, bg_width)
    """
    full_mask = np.zeros((bg_height, bg_width), dtype=np.uint8)
    
    x, y = position
    h, w = fg_mask.shape
    
    # Calculate valid paste region
    x_start = max(0, x)
    y_start = max(0, y)
    x_end = min(bg_width, x + w)
    y_end = min(bg_height, y + h)
    
    # Calculate corresponding region in foreground mask
    fg_x_start = max(0, -x)
    fg_y_start = max(0, -y)
    fg_x_end = fg_x_start + (x_end - x_start)
    fg_y_end = fg_y_start + (y_end - y_start)
    
    # Paste mask
    full_mask[y_start:y_end, x_start:x_end] = fg_mask[fg_y_start:fg_y_end, fg_x_start:fg_x_end]
    
    return full_mask
