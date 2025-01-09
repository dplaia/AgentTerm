import tkinter as tk
from PIL import ImageGrab
import pyautogui
import os
import time
from threading import Thread

# Create screenshots directory if it doesn't exist
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

class ContinuousCapture:
    def __init__(self):
        self.running = False
        self.root = None
        self.capture_thread = None
        self.rect_coords = (0, 0, 400, 300)  # Default size

    def start_capture(self):
        self.root = tk.Tk()
        self.root.title("Continuous Capture")
        
        # Set initial window size and position
        self.root.geometry("400x300")
        
        # Make window background transparent while keeping title bar
        self.root.attributes('-transparentcolor', 'gray')
        self.root.attributes('-topmost', True)  # Keep window on top
        
        # Create a resizable rectangle with transparent background
        self.canvas = tk.Canvas(
            self.root, 
            width=400, 
            height=300, 
            highlightthickness=0,
            bg='gray'  # This color will be made transparent
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.rect = self.canvas.create_rectangle(0, 0, 400, 300, outline="blue", width=8)
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Bind window resize event
        self.root.bind("<Configure>", self.on_resize)
        
        # Start capture thread
        self.running = True
        self.capture_thread = Thread(target=self.capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_resize(self, event):
        # Only update if it's a window resize event (not other configure events)
        if event.widget == self.root:
            # Update canvas size
            self.canvas.config(width=event.width, height=event.height)
            # Update rectangle size
            self.canvas.coords(self.rect, 0, 0, event.width, event.height)
            # Store current coordinates using screen coordinates
            self.rect_coords = (
                self.root.winfo_rootx(),  # Get absolute screen x
                self.root.winfo_rooty(),  # Get absolute screen y
                self.root.winfo_rootx() + event.width,
                self.root.winfo_rooty() + event.height
            )

    def capture_loop(self):
        counter = 0
        while self.running:
            try:
                # Get the window coordinates in screen space
                x1 = self.root.winfo_rootx()
                y1 = self.root.winfo_rooty()
                x2 = x1 + self.root.winfo_width()
                y2 = y1 + self.root.winfo_height()
                
                # Adjust coordinates to exclude window decorations
                border_width = 8
                title_bar_height = 10  # Standard Windows title bar height
                
                # Adjust to capture only the inside of the blue rectangle
                x1 += border_width
                y1 += title_bar_height  # Only add title bar height, not border
                x2 -= border_width
                y2 -= border_width
                
                # Ensure valid capture area
                if x2 > x1 and y2 > y1:
                    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                    screenshot.save(f"screenshots/capture_{counter}.png")
                    counter += 1
                time.sleep(1)
            except Exception as e:
                print(f"Error during capture: {e}")
                time.sleep(1)

    def on_closing(self):
        self.running = False
        if self.capture_thread:
            self.capture_thread.join()
        self.root.destroy()

class ScreenshotTool:
    def __init__(self):
        self.start_x = 0
        self.start_y = 0
        
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.root.configure(cursor="cross")

        self.canvas = tk.Canvas(self.root, bg="gray", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.rect = self.canvas.create_rectangle(0, 0, 0, 0, outline="blue", width=8)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<KeyPress-s>", lambda e: self.take_screenshot())

    def take_screenshot(self):
        self.root.withdraw()
        screen = pyautogui.screenshot()
        screen.save("full_screenshot.png")
        self.root.deiconify()

    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_mouse_release(self, event):
        end_x, end_y = event.x, event.y
        self.root.withdraw()
        
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        region = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        region.save("cropped_screenshot.png")
        
        self.root.destroy()

    def on_mouse_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.start_x, self.start_y)

    def start(self):
        self.root.mainloop()

def main():
    print("Select mode:")
    print("1. Screenshot Tool (Original mode)")
    print("2. Continuous Capture (Green rectangle mode)")
    
    #mode = input("Enter mode (1 or 2): ")
    mode = "2"
    if mode == "1":
        tool = ScreenshotTool()
        tool.start()
    elif mode == "2":
        capture = ContinuousCapture()
        capture.start_capture()
    else:
        print("Invalid mode selected")

if __name__ == "__main__":
    # # Delete screenshots directory (debug )
    # if os.path.exists("screenshots"):
    #     import shutil
    #     shutil.rmtree("screenshots")
    main()
