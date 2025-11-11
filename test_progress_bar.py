"""
Test script to verify progress bar updates work correctly
"""
import tkinter as tk
from tkinter import ttk
import time
import threading

def test_progress_bar():
    root = tk.Tk()
    root.title("Progress Bar Test")
    root.geometry("400x200")
    
    progress_var = tk.StringVar(value="Ready")
    ttk.Label(root, textvariable=progress_var).pack(pady=10)
    
    progress_bar = ttk.Progressbar(root, mode='determinate', maximum=100, length=300)
    progress_bar.pack(pady=10)
    
    percent_var = tk.StringVar(value="")
    ttk.Label(root, textvariable=percent_var, font=("Arial", 12, "bold")).pack()
    
    def update_progress(percent):
        """Test progress bar update"""
        progress_bar['value'] = percent
        progress_bar.config(value=percent)
        percent_var.set(f"{int(percent)}%")
        progress_var.set(f"Progress: {int(percent)}%")
        root.update_idletasks()
        print(f"Progress bar updated to {int(percent)}%")
    
    def simulate_work():
        """Simulate work with progress updates"""
        for i in range(0, 101, 5):
            root.after(0, lambda p=i: update_progress(p))
            time.sleep(0.2)
    
    # Start simulation
    thread = threading.Thread(target=simulate_work, daemon=True)
    thread.start()
    
    root.mainloop()

if __name__ == "__main__":
    test_progress_bar()

