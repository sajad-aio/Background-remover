import customtkinter as ctk
from rembg import remove
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
from io import BytesIO


class BackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Background Remover with Advanced Features")
        self.root.geometry("1000x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Sidebar frame
        self.sidebar = ctk.CTkFrame(root, width=250, height=600, corner_radius=15)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        # Canvas for displaying images
        self.canvas = ctk.CTkCanvas(root, width=700, height=550, bg="#333333")
        self.canvas.pack(side="right", padx=10, pady=10)

        # Sidebar content
        self.upload_button = ctk.CTkButton(self.sidebar, text="Upload User Image", corner_radius=15,
                                           command=lambda: [self.animate_button(self.upload_button),
                                                            self.upload_user_image()])
        self.upload_button.pack(pady=10)

        self.upload_bg_button = ctk.CTkButton(self.sidebar, text="Upload Background Image", corner_radius=15,
                                              command=lambda: [self.animate_button(self.upload_bg_button),
                                                               self.upload_bg_image()])
        self.upload_bg_button.pack(pady=10)

        self.result_button = ctk.CTkButton(self.sidebar, text="Generate & Save", corner_radius=15,
                                           command=self.generate_and_save_image, state="disabled")
        self.result_button.pack(pady=10)

        # Zoom slider
        ctk.CTkLabel(self.sidebar, text="Zoom Image", font=("Arial", 14)).pack(pady=5)
        self.zoom_slider = ctk.CTkSlider(self.sidebar, from_=0.5, to=2, command=self.update_zoom)
        self.zoom_slider.set(1)  # Default zoom is 1
        self.zoom_slider.pack(pady=10)

        # Filter buttons
        self.blur_button = ctk.CTkButton(self.sidebar, text="Apply Blur Effect", corner_radius=15,
                                         command=lambda: self.apply_filter("blur"))
        self.blur_button.pack(pady=10)

        self.brightness_button = ctk.CTkButton(self.sidebar, text="Increase Brightness", corner_radius=15,
                                               command=lambda: self.apply_filter("brightness"))
        self.brightness_button.pack(pady=10)

        # Position adjustment
        ctk.CTkLabel(self.sidebar, text="Adjust Position", font=("Arial", 14)).pack(pady=5)
        self.x_entry = ctk.CTkEntry(self.sidebar, placeholder_text="X Position")
        self.x_entry.pack(pady=5)
        self.y_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Y Position")
        self.y_entry.pack(pady=5)

        self.set_position_button = ctk.CTkButton(self.sidebar, text="Set Position", corner_radius=15,
                                                 command=self.set_position_from_entry)
        self.set_position_button.pack(pady=10)

        # Initialize attributes
        self.user_image = None
        self.bg_image = None
        self.user_image_resized = None
        self.user_position = [0, 0]

        # Canvas binding for dragging user image
        self.canvas.bind("<B1-Motion>", self.move_image)
        self.canvas.bind("<ButtonPress-1>", self.set_initial_position)

    def animate_button(self, button):
        original_color = button.cget("fg_color")
        button.configure(fg_color="#ffcc00")
        self.root.after(200, lambda: button.configure(fg_color=original_color))

    def upload_user_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, "rb") as f:
                self.user_image = Image.open(BytesIO(remove(f.read()))).convert("RGBA")
            self.user_image_resized = self.user_image.copy()
            self.check_images()

    def upload_bg_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.bg_image = Image.open(file_path).convert("RGBA").resize((700, 550))
            self.check_images()

    def check_images(self):
        if self.user_image and self.bg_image:
            self.result_button.configure(state="normal")
            self.update_composite_image()

    def set_initial_position(self, event):
        self.user_position = [event.x, event.y]

    def move_image(self, event):
        dx = event.x - self.user_position[0]
        dy = event.y - self.user_position[1]
        self.user_position[0] += dx
        self.user_position[1] += dy
        self.update_composite_image()

    def update_zoom(self, scale):
        if self.user_image:
            new_size = (int(self.user_image.width * scale), int(self.user_image.height * scale))
            self.user_image_resized = self.user_image.resize(new_size)
            self.update_composite_image()

    def apply_filter(self, filter_type):
        if self.bg_image:
            if filter_type == "blur":
                self.bg_image = self.bg_image.filter(ImageFilter.BLUR)
            elif filter_type == "brightness":
                enhancer = ImageEnhance.Brightness(self.bg_image)
                self.bg_image = enhancer.enhance(1.5)
            self.update_composite_image()

    def set_position_from_entry(self):
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            self.user_position = [x, y]
            self.update_composite_image()
        except ValueError:
            pass

    def update_composite_image(self):
        if self.bg_image and self.user_image_resized:
            composite = self.bg_image.copy()
            position = (self.user_position[0], self.user_position[1])
            composite.paste(self.user_image_resized, position, self.user_image_resized)
            self.composite_image = ImageTk.PhotoImage(composite)
            self.canvas.create_image(0, 0, anchor="nw", image=self.composite_image)

    def generate_and_save_image(self):
        if self.bg_image and self.user_image_resized:
            composite = self.bg_image.copy()
            position = (self.user_position[0], self.user_position[1])
            composite.paste(self.user_image_resized, position, self.user_image_resized)
            composite.save("output_image.png")
            composite.show()


root = ctk.CTk()
app = BackgroundRemoverApp(root)
root.mainloop()
