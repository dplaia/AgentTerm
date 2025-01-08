import tkinter as tk
from PIL import ImageGrab
import pyautogui

def take_screenshot():
    # Hide the root window for capturing the entire screen
    root.withdraw()
    
    # Capture the entire screen
    screen = pyautogui.screenshot()
    screen.save("full_screenshot.png")  # Save the entire screenshot for reference
    
    # Show the root window again
    root.deiconify()

def on_mouse_drag(event):
    # Update rectangle dimensions as the mouse is dragged
    canvas.coords(rect, start_x, start_y, event.x, event.y)

def on_mouse_release(event):
    # Get final coordinates of the selection rectangle
    end_x, end_y = event.x, event.y
    root.withdraw()  # Hide the Tkinter window for capturing
    
    # Calculate the coordinates for cropping
    x1 = min(start_x, end_x)
    y1 = min(start_y, end_y)
    x2 = max(start_x, end_x)
    y2 = max(start_y, end_y)
    
    # Take a screenshot of the specified region
    region = ImageGrab.grab(bbox=(x1, y1, x2, y2))  # bbox = (left, top, right, bottom)
    region.save("cropped_screenshot.png")  # Save the cropped screenshot
    
    root.destroy()  # Close the Tkinter window

def on_mouse_press(event):
    global start_x, start_y
    start_x, start_y = event.x, event.y
    canvas.coords(rect, start_x, start_y, start_x, start_y)

# Set up Tkinter
root = tk.Tk()
root.attributes('-fullscreen', True)  # Make the window full screen
root.attributes('-alpha', 0.3)  # Make the window transparent
root.configure(cursor="cross")  # Change cursor to a cross

# Canvas to display the selection rectangle
canvas = tk.Canvas(root, bg="gray", highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

# Add a rectangle on the canvas
rect = canvas.create_rectangle(0, 0, 0, 0, outline="red", width=5)

# Bind mouse events
canvas.bind("<ButtonPress-1>", on_mouse_press)
canvas.bind("<B1-Motion>", on_mouse_drag)
canvas.bind("<ButtonRelease-1>", on_mouse_release)

# Optional: Add a keybind for capturing the entire screen
root.bind("<Escape>", lambda e: root.destroy())  # Exit on pressing Esc
root.bind("<KeyPress-s>", lambda e: take_screenshot())  # Take full screenshot with 's'

root.mainloop()
