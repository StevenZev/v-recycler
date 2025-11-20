"""
Generate simple ground texture backgrounds (asphalt, grass, dirt).
Creates synthetic background images for testing without needing to download external images.
"""

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import random
from pathlib import Path
import argparse
from tqdm import tqdm


def generate_asphalt_texture(width: int = 1024, height: int = 1024, seed: int = None) -> Image.Image:
    """
    Generate a realistic asphalt texture.
    
    Args:
        width: Image width
        height: Image height
        seed: Random seed for reproducibility
        
    Returns:
        PIL Image of asphalt texture
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Base dark gray color with variation
    base_value = random.randint(40, 60)
    
    # Create base noise
    texture = np.random.randint(
        base_value - 15, 
        base_value + 15, 
        (height, width, 3), 
        dtype=np.uint8
    )
    
    # Add larger noise patterns for aggregate appearance
    large_noise = np.random.randint(-10, 10, (height // 4, width // 4, 3))
    large_noise = np.kron(large_noise, np.ones((4, 4, 1))).astype(np.int16)
    texture = np.clip(texture.astype(np.int16) + large_noise[:height, :width], 0, 255).astype(np.uint8)
    
    # Convert to PIL and apply filters
    img = Image.fromarray(texture, 'RGB')
    
    # Slight blur for more realistic appearance
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Adjust contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(random.uniform(1.1, 1.3))
    
    # Add some brightness variation
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(random.uniform(0.9, 1.1))
    
    return img


def generate_grass_texture(width: int = 1024, height: int = 1024, seed: int = None) -> Image.Image:
    """
    Generate a grass texture.
    
    Args:
        width: Image width
        height: Image height
        seed: Random seed for reproducibility
        
    Returns:
        PIL Image of grass texture
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Base green colors with variation
    base_green = random.randint(60, 90)
    base_red = random.randint(20, 40)
    base_blue = random.randint(20, 40)
    
    # Create channels separately for more color variation
    r_channel = np.random.randint(base_red - 10, base_red + 20, (height, width), dtype=np.uint8)
    g_channel = np.random.randint(base_green - 20, base_green + 30, (height, width), dtype=np.uint8)
    b_channel = np.random.randint(base_blue - 10, base_blue + 20, (height, width), dtype=np.uint8)
    
    texture = np.stack([r_channel, g_channel, b_channel], axis=-1)
    
    # Add patches of different green shades
    for _ in range(random.randint(5, 15)):
        patch_size = random.randint(50, 200)
        x = random.randint(0, width - patch_size)
        y = random.randint(0, height - patch_size)
        
        patch_variation = random.randint(-30, 30)
        texture[y:y+patch_size, x:x+patch_size, 1] = np.clip(
            texture[y:y+patch_size, x:x+patch_size, 1].astype(np.int16) + patch_variation,
            0, 255
        ).astype(np.uint8)
    
    # Convert to PIL and apply filters
    img = Image.fromarray(texture, 'RGB')
    
    # Blur for softer appearance
    img = img.filter(ImageFilter.GaussianBlur(radius=1.0))
    
    # Add some texture noise back
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(random.uniform(1.3, 1.6))
    
    # Adjust saturation
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(random.uniform(0.8, 1.2))
    
    return img


def generate_dirt_texture(width: int = 1024, height: int = 1024, seed: int = None) -> Image.Image:
    """
    Generate a dirt/soil texture.
    
    Args:
        width: Image width
        height: Image height
        seed: Random seed for reproducibility
        
    Returns:
        PIL Image of dirt texture
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Base brown/tan color
    base_r = random.randint(100, 130)
    base_g = random.randint(70, 100)
    base_b = random.randint(40, 70)
    
    # Create base texture with variation
    r_channel = np.random.randint(base_r - 30, base_r + 30, (height, width), dtype=np.uint8)
    g_channel = np.random.randint(base_g - 30, base_g + 30, (height, width), dtype=np.uint8)
    b_channel = np.random.randint(base_b - 20, base_b + 20, (height, width), dtype=np.uint8)
    
    texture = np.stack([r_channel, g_channel, b_channel], axis=-1)
    
    # Add rocky patches (lighter/darker spots)
    for _ in range(random.randint(10, 30)):
        patch_size = random.randint(20, 100)
        x = random.randint(0, width - patch_size)
        y = random.randint(0, height - patch_size)
        
        if random.random() > 0.5:
            # Lighter rock
            variation = random.randint(20, 40)
        else:
            # Darker spot
            variation = random.randint(-40, -20)
        
        for c in range(3):
            texture[y:y+patch_size, x:x+patch_size, c] = np.clip(
                texture[y:y+patch_size, x:x+patch_size, c].astype(np.int16) + variation,
                0, 255
            ).astype(np.uint8)
    
    # Convert to PIL and apply filters
    img = Image.fromarray(texture, 'RGB')
    
    # Add medium blur
    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
    
    # Enhance contrast for gritty appearance
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(random.uniform(1.2, 1.4))
    
    # Slight brightness variation
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(random.uniform(0.9, 1.1))
    
    return img


def generate_backgrounds(
    output_folder: str = "data/raw/backgrounds",
    num_each: int = 20,
    width: int = 1024,
    height: int = 1024,
):
    """
    Generate a set of ground texture backgrounds.
    
    Args:
        output_folder: Output folder for generated images
        num_each: Number of each texture type to generate
        width: Image width
        height: Image height
    """
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating ground texture backgrounds...")
    print(f"Output: {output_folder}")
    print(f"Size: {width}x{height}")
    print(f"Count per type: {num_each}")
    print()
    
    total = num_each * 3
    
    with tqdm(total=total, desc="Generating backgrounds") as pbar:
        # Generate asphalt textures
        for i in range(num_each):
            img = generate_asphalt_texture(width, height, seed=i)
            filename = output_path / f"asphalt_{i:03d}.jpg"
            img.save(filename, quality=95)
            pbar.update(1)
        
        # Generate grass textures
        for i in range(num_each):
            img = generate_grass_texture(width, height, seed=i + 1000)
            filename = output_path / f"grass_{i:03d}.jpg"
            img.save(filename, quality=95)
            pbar.update(1)
        
        # Generate dirt textures
        for i in range(num_each):
            img = generate_dirt_texture(width, height, seed=i + 2000)
            filename = output_path / f"dirt_{i:03d}.jpg"
            img.save(filename, quality=95)
            pbar.update(1)
    
    print(f"\n{'='*60}")
    print(f"Background generation complete!")
    print(f"Total images: {total}")
    print(f"  - Asphalt: {num_each}")
    print(f"  - Grass: {num_each}")
    print(f"  - Dirt: {num_each}")
    print(f"Output folder: {output_folder}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate ground texture backgrounds (asphalt, grass, dirt)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/raw/backgrounds',
        help='Output folder for generated backgrounds'
    )
    parser.add_argument(
        '--num-each',
        type=int,
        default=20,
        help='Number of each texture type to generate (default: 20)'
    )
    parser.add_argument(
        '--width',
        type=int,
        default=1024,
        help='Image width (default: 1024)'
    )
    parser.add_argument(
        '--height',
        type=int,
        default=1024,
        help='Image height (default: 1024)'
    )
    
    args = parser.parse_args()
    
    generate_backgrounds(
        output_folder=args.output,
        num_each=args.num_each,
        width=args.width,
        height=args.height,
    )


if __name__ == '__main__':
    main()
