import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import time
import cv2

from processing import ImageProcessor


class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing App with PyTorch")
        self.root.geometry("900x800")

        self.processor = ImageProcessor()

        self.display_size = (800, 600)
        self.cap = None
        self.webcam_running = False
        self.current_frame = None
        self.camera_thread = None

        self.image_frame = tk.Frame(root, width=self.display_size[0], height=self.display_size[1], bg="gray")
        self.image_frame.pack(padx=10, pady=10)

        self.label = tk.Label(self.image_frame)
        self.label.pack()

        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(padx=10, pady=10)

        tk.Button(self.controls_frame, text="Загрузить изображение", command=self.load_image).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(self.controls_frame, text="Включить камеру", command=self.start_webcam).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.controls_frame, text="Сделать снимок", command=self.take_snapshot).grid(row=0, column=2, padx=5, pady=5)

        self.channel_var = tk.StringVar(value="R")
        tk.OptionMenu(self.controls_frame, self.channel_var, "R", "G", "B", command=self.show_channel).grid(row=1, column=0, padx=5, pady=5)

        tk.Button(self.controls_frame, text="Оттенки серого", command=self.to_grayscale).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.controls_frame, text="Угол поворота:").grid(row=1, column=2, padx=5, pady=5)
        self.angle_entry = tk.Entry(self.controls_frame, width=5)
        self.angle_entry.grid(row=1, column=3, padx=5)
        self.angle_entry.insert(0, "0")
        tk.Button(self.controls_frame, text="Повернуть", command=self.rotate_image).grid(row=1, column=4, padx=5, pady=5)

        tk.Label(self.controls_frame, text="Координаты (x1,y1,x2,y2):").grid(row=2, column=0, padx=5, pady=5)
        self.coord_entry = tk.Entry(self.controls_frame, width=20)
        self.coord_entry.grid(row=2, column=1, padx=5, pady=5)
        self.coord_entry.insert(0, "10,10,100,100")
        tk.Button(self.controls_frame, text="Нарисовать прямоугольник", command=self.draw_rectangle).grid(row=2, column=2, padx=5, pady=5)

        tk.Button(self.controls_frame, text="Сбросить", command=self.reset_app).grid(row=2, column=3, padx=5, pady=5)
        
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self.controls_frame, textvariable=self.status_var, fg="blue")
        self.status_label.grid(row=3, column=0, columnspan=5, pady=5)

    def display_image(self, image):
        img = image.copy()
        img.thumbnail(self.display_size, Image.LANCZOS)
        self.img_tk = ImageTk.PhotoImage(img)
        self.label.config(image=self.img_tk)
        self.label.image = self.img_tk

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if not path:
            return
        try:
            image = Image.open(path).convert("RGB")
            self.processor.set_image(image)
            self.display_image(image)
            self.status_var.set("Изображение загружено")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{e}")

    def init_webcam(self):
        self.status_var.set("Инициализация камеры...")
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cap.isOpened():
                self.root.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось открыть камеру"))
                return

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            time.sleep(0.5)

            self.cap = cap
            self.webcam_running = True
            self.root.after(0, lambda: self.status_var.set("Камера запущена"))
            self.update_frame()
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка инициализации камеры:\n{e}"))

    def start_webcam(self):
        if self.webcam_running:
            return
        self.camera_thread = threading.Thread(target=self.init_webcam, daemon=True)
        self.camera_thread.start()

    def update_frame(self):
        if not self.webcam_running or self.cap is None:
            return
        try:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.current_frame = Image.fromarray(frame)
                self.display_image(self.current_frame)
        except Exception as e:
            print(f"Ошибка при обновлении кадра: {e}")
            self.stop_webcam()
            return
        self.root.after(30, self.update_frame)

    def take_snapshot(self):
        if self.current_frame is None:
            messagebox.showinfo("Информация", "Нет доступного кадра")
            return
        self.processor.set_image(self.current_frame.copy())
        self.display_image(self.current_frame)
        self.stop_webcam()

    def stop_webcam(self):
        self.webcam_running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.status_var.set("Камера остановлена")

    def show_channel(self, channel):
        img = self.processor.show_channel(channel)
        if img is not None:
            self.display_image(img)

    def to_grayscale(self):
        img = self.processor.to_grayscale()
        if img is not None:
            self.display_image(img)

    def rotate_image(self):
        try:
            angle = float(self.angle_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный угол (например, 45)")
            return
        img = self.processor.rotate_image(angle)
        if img is not None:
            self.display_image(img)

    def draw_rectangle(self):
        try:
            coords = list(map(int, self.coord_entry.get().split(",")))
            if len(coords) != 4:
                raise ValueError
        except Exception:
            messagebox.showerror("Ошибка", "Введите координаты в формате: x1,y1,x2,y2")
            return
        img = self.processor.draw_rectangle(coords)
        if img is not None:
            self.display_image(img)

    def reset_app(self):
        self.stop_webcam()
        self.processor.reset()
        self.label.config(image="")
        self.channel_var.set("R")
        self.angle_entry.delete(0, tk.END)
        self.angle_entry.insert(0, "0")
        self.coord_entry.delete(0, tk.END)
        self.coord_entry.insert(0, "10,10,100,100")
        self.status_var.set("")
        messagebox.showinfo("Сброс", "Приложение сброшено в исходное состояние")
