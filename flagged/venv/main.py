import customtkinter as ctk
from tkinter import filedialog, colorchooser, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont

# Global variables to track selected text
selected_text_id = None
text_boxes = {}

# Function to open an image file
def open_image():
    filepath = filedialog.askopenfilename()
    if filepath:
        img = Image.open(filepath)
        img.thumbnail((400, 400))
        global img_display, img_original, draw
        img_original = img.copy()
        draw = ImageDraw.Draw(img_original)
        img_display = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor="nw", image=img_display)
def add_text(x, y):
    text = text_entry.get()
    text_color = color_var.get()
    bg_color = bg_color_var.get()
    size = int(size_entry.get())

    # Create font for PIL and canvas
    font_style = ImageFont.truetype("arial.ttf", size)
    canvas_font = ("Arial", size)

    # Create a temporary text to measure its size
    temp_text = canvas.create_text(0, 0, text=text, font=canvas_font, anchor="nw")
    text_bbox = canvas.bbox(temp_text)  # Get the bounding box of the text
    canvas.delete(temp_text)  # Remove the temporary text

    # Calculate text dimensions
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Add consistent padding around the text
    padding_x = 10  # Horizontal padding
    padding_y = 5   # Vertical padding

    # Coordinates for the cloud's bounding area
    cloud_left = x - padding_x
    cloud_top = y - padding_y
    cloud_right = x + text_width + padding_x
    cloud_bottom = y + text_height + padding_y

    # Create the cloud shape
    cloud_radius = 10  # Radius for cloud-like curves
    steps = [
        # Top-left corner
        (cloud_left, cloud_top, cloud_left + 2 * cloud_radius, cloud_top + 2 * cloud_radius),
        # Top-right corner
        (cloud_right - 2 * cloud_radius, cloud_top, cloud_right, cloud_top + 2 * cloud_radius),
        # Bottom-left corner
        (cloud_left, cloud_bottom - 2 * cloud_radius, cloud_left + 2 * cloud_radius, cloud_bottom),
        # Bottom-right corner
        (cloud_right - 2 * cloud_radius, cloud_bottom - 2 * cloud_radius, cloud_right, cloud_bottom),
    ]

    # Draw rounded parts of the cloud
    for step in steps:
        canvas.create_oval(step, fill=bg_color, outline="")

    # Draw the straight parts of the cloud
    canvas.create_rectangle(
        cloud_left + cloud_radius, cloud_top, cloud_right - cloud_radius, cloud_bottom,
        fill=bg_color, outline=""
    )
    canvas.create_rectangle(
        cloud_left, cloud_top + cloud_radius, cloud_right, cloud_bottom - cloud_radius,
        fill=bg_color, outline=""
    )

    # Draw the text on the canvas
    canvas_text = canvas.create_text(
        x, y,
        text=text, fill=text_color, font=canvas_font, anchor="nw"
    )

    # Store the text box details, including the cloud
    text_boxes[canvas_text] = {
        "text": text,
        "text_color": text_color,
        "bg_color": bg_color,
        "size": size,
        "font": font_style,
        "cloud_radius": cloud_radius,
    }

# Function to handle right-click to add text
def right_click(event):
    add_text(event.x, event.y)

# Function to select text on click
def select_text(event):
    global selected_text_id
    item = canvas.find_closest(event.x, event.y)[0]
    if item in text_boxes:
        if selected_text_id:
            canvas.itemconfig(selected_text_id, outline="")  # Remove highlight from previous selection
        selected_text_id = item
        canvas.itemconfig(selected_text_id, outline="red")  # Highlight current selection

# Function to start dragging
def start_drag(event):
    select_text(event)
    canvas.tag_bind(selected_text_id, "<B1-Motion>", drag_text)

# Function to drag text and background
def drag_text(event):
    if selected_text_id:
        bg_rect = text_boxes[selected_text_id]["bg_rect"]
        x, y = event.x, event.y
        width, height = canvas.bbox(selected_text_id)[2:]
        canvas.coords(bg_rect, x, y, x + width + 10, y + height + 5)
        canvas.coords(selected_text_id, x + 5, y + 2)

# Function to edit text inline
def edit_text(event):
    global selected_text_id
    if selected_text_id:
        text = simpledialog.askstring("Edit Text", "Enter new text:", initialvalue=canvas.itemcget(selected_text_id, "text"))
        if text:
            canvas.itemconfig(selected_text_id, text=text)
            text_boxes[selected_text_id]["text"] = text

# Function to pick text color
def pick_color():
    color = colorchooser.askcolor()[1]
    if color:
        color_var.set(color)

# Function to pick background color
def pick_bg_color():
    bg_color = colorchooser.askcolor()[1]
    if bg_color:
        bg_color_var.set(bg_color)


# Function to save the edited image
def save_image():
    save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if save_path:
        for text_id, data in text_boxes.items():
            x, y = canvas.coords(text_id)
            draw.rectangle([x, y, x + 100, y + 50], fill=data["bg_color"])  # Adjust to actual bounds
            draw.text((x + 5, y + 2), data["text"], fill=data["text_color"], font=data["font"])
        img_original.save(save_path)

# Create main window
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Image Text Adder")
root.geometry("700x550")

canvas_frame = ctk.CTkFrame(root)
canvas_frame.grid(row=0, column=0)

# Create canvas for image
canvas = ctk.CTkCanvas(canvas_frame, width=400, height=400, bg='gray')
canvas.grid(row=0, column=0, pady=10, padx=10)
canvas.bind("<Button-3>", right_click)  # Right-click to add text
canvas.bind("<Button-1>", start_drag)   # Left-click to select/drag
canvas.bind("<Double-Button-1>", edit_text)  # Double-click to edit text

# Open image button
open_button = ctk.CTkButton(canvas_frame, text="Open Image", command=open_image)
open_button.grid(row=1, column=0, pady=10)

frame = ctk.CTkFrame(root)
frame.grid(row=0, column=1, pady=10, padx=30)

# Text input
text_label = ctk.CTkLabel(frame, text="Text:")
text_label.grid(row=0, column=0)
text_entry = ctk.CTkEntry(frame, placeholder_text="Enter text here")
text_entry.grid(row=1, column=0, pady=5)

# Font size input
size_label = ctk.CTkLabel(frame, text="Font Size:")
size_label.grid(row=2, column=0)
size_entry = ctk.CTkEntry(frame, placeholder_text="Font size")
size_entry.grid(row=3, column=0, pady=5)

# Color picker
color_label = ctk.CTkLabel(frame, text="Color:")
color_label.grid(row=4, column=0)
color_var = ctk.StringVar(value="black")
color_entry = ctk.CTkEntry(frame, textvariable=color_var)
color_entry.grid(row=5, column=0, pady=5)
color_button = ctk.CTkButton(frame, text="Pick Color", command=pick_color)
color_button.grid(row=6, column=0)

# Background color picker
bg_color_label = ctk.CTkLabel(frame, text="Background Color:")
bg_color_label.grid(row=7, column=0)
bg_color_var = ctk.StringVar(value="white")
bg_color_entry = ctk.CTkEntry(frame, textvariable=bg_color_var)
bg_color_entry.grid(row=8, column=0, pady=5)
bg_color_button = ctk.CTkButton(frame, text="Pick Background Color", command=pick_bg_color)
bg_color_button.grid(row=9, column=0)

# Save image button
save_button = ctk.CTkButton(root, text="Save Image", command=save_image)
save_button.grid(row=1, column=0, columnspan=2, pady=10)

root.mainloop()

