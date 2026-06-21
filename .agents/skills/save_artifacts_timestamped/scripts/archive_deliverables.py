import os
import shutil
from datetime import datetime

def archive():
    src_dir = "simulation_results"
    archive_root = "archives"
    
    if not os.path.exists(src_dir):
        print(f"Error: Source directory '{src_dir}' does not exist.")
        return
        
    # Get YYYYMMDDhhmmss timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    dest_dir = os.path.join(archive_root, timestamp)
    
    os.makedirs(dest_dir, exist_ok=True)
    
    # Copy files
    copied_files = []
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        dest_path = os.path.join(dest_dir, item)
        
        if os.path.isfile(src_path):
            shutil.copy2(src_path, dest_path)
            copied_files.append(item)
            
    print(f"SUCCESS: Archived {len(copied_files)} files to {os.path.abspath(dest_dir)}")
    for f in copied_files:
        print(f" - {f}")

if __name__ == "__main__":
    archive()
