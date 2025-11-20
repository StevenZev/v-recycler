"""
Download TrashNet dataset from Hugging Face.
"""

import argparse
from pathlib import Path
from datasets import load_dataset
from PIL import Image
from tqdm import tqdm


def download_trashnet(output_folder: str = "data/raw/trashnet"):
    """
    Download TrashNet dataset from Hugging Face and organize by class.
    
    Args:
        output_folder: Output folder for TrashNet images
    """
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("Downloading TrashNet dataset from Hugging Face...")
    print("Dataset: garythung/trashnet")
    print()
    
    # Load dataset
    dataset = load_dataset("garythung/trashnet", split="train")
    
    print(f"Total images: {len(dataset)}")
    print()
    
    # Class folders
    class_counts = {}
    
    # Process each image
    for idx, item in enumerate(tqdm(dataset, desc="Downloading and organizing")):
        image = item['image']
        label = item['label']
        
        # Get class name from label
        # TrashNet classes: cardboard, glass, metal, paper, plastic, trash
        class_names = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']
        class_name = class_names[label]
        
        # Create class folder
        class_folder = output_path / class_name
        class_folder.mkdir(exist_ok=True)
        
        # Save image
        image_filename = f"{class_name}_{idx:04d}.jpg"
        image_path = class_folder / image_filename
        
        if isinstance(image, Image.Image):
            image.save(image_path)
        else:
            # Convert to PIL Image if needed
            Image.fromarray(image).save(image_path)
        
        # Update counts
        class_counts[class_name] = class_counts.get(class_name, 0) + 1
    
    print(f"\n{'='*60}")
    print("Download complete!")
    print(f"Output folder: {output_folder}")
    print("\nImages per class:")
    for class_name, count in sorted(class_counts.items()):
        print(f"  {class_name}: {count}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description='Download TrashNet dataset from Hugging Face')
    parser.add_argument(
        '--output',
        type=str,
        default='data/raw/trashnet',
        help='Output folder for TrashNet images (default: data/raw/trashnet)'
    )
    
    args = parser.parse_args()
    
    try:
        download_trashnet(args.output)
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure you have the 'datasets' package installed:")
        print("  pip install datasets")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
