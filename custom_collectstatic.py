# custom_collectstatic.py
import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_SOURCES = [
    BASE_DIR / 'static',
    BASE_DIR / 'home' / 'static',
    BASE_DIR / 'accounts' / 'static',
    BASE_DIR / 'products' / 'static',
    BASE_DIR / 'cart' / 'static',
    BASE_DIR / 'orders' / 'static',
    BASE_DIR / 'payments' / 'static',
]

def collect_static():
    # Clear staticfiles directory
    if STATIC_ROOT.exists():
        shutil.rmtree(STATIC_ROOT)
    STATIC_ROOT.mkdir(parents=True, exist_ok=True)
    
    copied_files = 0
    
    # Copy from all sources
    for source_dir in STATIC_SOURCES:
        if source_dir.exists():
            for item in source_dir.rglob('*'):
                if item.is_file():
                    # Calculate relative path
                    rel_path = item.relative_to(source_dir)
                    dest_path = STATIC_ROOT / rel_path
                    
                    # Create destination directory
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(item, dest_path)
                    copied_files += 1
                    
                    print(f'Copied: {rel_path}')
    
    print(f'\n✅ Total {copied_files} static files collected')
    print(f'📍 Static files saved to: {STATIC_ROOT}')

if __name__ == '__main__':
    collect_static()