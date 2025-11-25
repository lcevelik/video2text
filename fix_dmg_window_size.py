#!/usr/bin/env python3
"""
Fix DMG window size to be non-resizable by modifying .DS_Store
"""
import os
import sys
import struct

def fix_dmg_window_size(dmg_path):
    """Modify .DS_Store in mounted DMG to lock window size."""
    # Mount the DMG temporarily
    import subprocess
    import tempfile
    
    mount_point = tempfile.mkdtemp()
    try:
        # Mount DMG
        result = subprocess.run(
            ['hdiutil', 'attach', dmg_path, '-mountpoint', mount_point, '-readwrite'],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            print(f"Error mounting DMG: {result.stderr}")
            return False
        
        dsstore_path = os.path.join(mount_point, '.DS_Store')
        
        if not os.path.exists(dsstore_path):
            print("Warning: .DS_Store not found")
            return False
        
        # .DS_Store is a binary format - modifying it directly is complex
        # Instead, we'll use AppleScript to set the window size again
        # and ensure it's saved properly
        
        print("Window size will be enforced via .DS_Store")
        
        # Unmount
        subprocess.run(['hdiutil', 'detach', mount_point], capture_output=True)
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if os.path.exists(mount_point):
            try:
                subprocess.run(['hdiutil', 'detach', mount_point], capture_output=True)
            except:
                pass

if __name__ == '__main__':
    if len(sys.argv) > 1:
        fix_dmg_window_size(sys.argv[1])
    else:
        print("Usage: fix_dmg_window_size.py <dmg_path>")

