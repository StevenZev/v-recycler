"""
Verify project setup and data availability.
"""

from pathlib import Path
import sys


def check_folder(path: Path, name: str, required: bool = True) -> tuple[bool, int]:
    """Check if folder exists and count files."""
    if not path.exists():
        if required:
            print(f"❌ {name}: NOT FOUND (required)")
            return False, 0
        else:
            print(f"⚠️  {name}: NOT FOUND (optional but recommended)")
            return False, 0
    
    # Count image files
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    count = sum(len(list(path.rglob(ext))) for ext in extensions)
    
    if count == 0:
        if required:
            print(f"❌ {name}: EMPTY (add images here)")
            return False, 0
        else:
            print(f"⚠️  {name}: EMPTY (add images here)")
            return False, 0
    
    print(f"✅ {name}: {count} images")
    return True, count


def main():
    print("=" * 60)
    print("V-RECYCLER PROJECT SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    base_path = Path('.')
    all_good = True
    
    # Check virtual environment
    venv_path = base_path / 'venv'
    if venv_path.exists():
        print("✅ Virtual environment: CREATED")
    else:
        print("❌ Virtual environment: NOT FOUND")
        print("   Run: python -m venv venv")
        all_good = False
    print()
    
    # Check required folders
    print("REQUIRED DATA:")
    print("-" * 60)
    
    trashnet_path = base_path / 'data' / 'raw' / 'trashnet'
    trashnet_ok, trashnet_count = check_folder(
        trashnet_path, 
        "TrashNet dataset (data/raw/trashnet)", 
        required=True
    )
    all_good = all_good and trashnet_ok
    
    if trashnet_ok:
        # Check individual classes
        expected_classes = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']
        for cls in expected_classes:
            cls_path = trashnet_path / cls
            if cls_path.exists():
                cls_count = len(list(cls_path.glob('*.jpg'))) + len(list(cls_path.glob('*.png')))
                print(f"   └─ {cls}: {cls_count} images")
    
    print()
    
    backgrounds_path = base_path / 'data' / 'raw' / 'backgrounds'
    bg_ok, bg_count = check_folder(
        backgrounds_path,
        "Background images (data/raw/backgrounds)",
        required=True
    )
    all_good = all_good and bg_ok
    
    if bg_ok and bg_count < 50:
        print("   ⚠️  Warning: Less than 50 backgrounds (recommended: 50-100)")
    
    print()
    print("GENERATED DATA (created by scripts):")
    print("-" * 60)
    
    foregrounds_path = base_path / 'data' / 'processed' / 'foregrounds'
    fg_ok, fg_count = check_folder(
        foregrounds_path,
        "Processed foregrounds (data/processed/foregrounds)",
        required=False
    )
    
    synthetic_images_path = base_path / 'data' / 'synthetic' / 'images'
    syn_ok, syn_count = check_folder(
        synthetic_images_path,
        "Synthetic images (data/synthetic/images)",
        required=False
    )
    
    synthetic_labels_path = base_path / 'data' / 'synthetic' / 'labels'
    if synthetic_labels_path.exists():
        label_count = len(list(synthetic_labels_path.glob('*.txt')))
        print(f"   └─ Labels: {label_count} files")
    
    print()
    print("=" * 60)
    
    if all_good:
        print("✅ SETUP COMPLETE - Ready to start data synthesis!")
        print()
        print("Next steps:")
        
        if not fg_ok:
            print("1. Extract foregrounds:")
            print("   .\\venv\\Scripts\\python.exe scripts\\extract_foregrounds.py")
        
        if not syn_ok:
            print("2. Generate synthetic scenes:")
            print("   .\\venv\\Scripts\\python.exe scripts\\generate_synthetic_scenes.py --num-scenes 1000")
        
        if fg_ok and syn_ok:
            print("All data ready! Proceed to training.")
            print("See: planning_docs/03_yolov8_seg_training_plan.md")
    else:
        print("⚠️  SETUP INCOMPLETE - Follow instructions above")
        print()
        print("Quick setup:")
        print("1. Create venv: python -m venv venv")
        print("2. Install deps: .\\venv\\Scripts\\python.exe -m pip install -r requirements.txt")
        print("3. Download TrashNet: .\\venv\\Scripts\\python.exe scripts\\download_trashnet.py")
        print("4. Add backgrounds to: data/raw/backgrounds/")
        print()
        print("See DATA_ACQUISITION.md for detailed instructions")
    
    print("=" * 60)
    
    return 0 if all_good else 1


if __name__ == '__main__':
    sys.exit(main())
