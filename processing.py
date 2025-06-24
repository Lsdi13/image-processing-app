from PIL import Image, ImageDraw
import torchvision.transforms as transforms
import torch

class ImageProcessor:
    def __init__(self):
        self.image_pil = None
        self.image_tensor = None
        self.original_tensor = None
        self.current_display_mode = None  

    def set_image(self, image: Image.Image):
        self.image_pil = image
        self.image_tensor = transforms.ToTensor()(image)
        self.original_tensor = self.image_tensor.clone()
        self.current_display_mode = None  

    def get_image(self):
        return self.image_pil

    def show_channel(self, channel):
        if self.original_tensor is None:
            return None
        

        ch_index = {"R": 0, "G": 1, "B": 2}[channel]
        zeros = torch.zeros_like(self.original_tensor)
        zeros[ch_index] = self.original_tensor[ch_index]
        img = transforms.ToPILImage()(zeros)
        

        self.image_pil = img
        self.image_tensor = zeros
        self.current_display_mode = f"channel_{channel}"
        
        return img
    
    def to_grayscale(self):
        if self.original_tensor is None:
            return None
        
   
        gray_tensor = self.original_tensor.mean(dim=0, keepdim=True).repeat(3, 1, 1)
        gray_pil = transforms.ToPILImage()(gray_tensor)
        
        self.image_pil = gray_pil
        self.image_tensor = gray_tensor
        self.current_display_mode = "grayscale"
        
        return gray_pil

    def rotate_image(self, angle):
        if self.image_pil is None:
            return None
        
        rotated = self.image_pil.rotate(angle, expand=True)
        
        # Обновляем все представления
        self.image_pil = rotated
        self.image_tensor = transforms.ToTensor()(rotated)
        

        if self.current_display_mode is None:
            self.original_tensor = self.image_tensor.clone()
        
        return rotated

    def draw_rectangle(self, coords):
        if self.image_pil is None:
            return None
        
        img_copy = self.image_pil.copy()
        draw = ImageDraw.Draw(img_copy)
        draw.rectangle(coords, outline="blue", width=3)
        
        self.image_pil = img_copy
        self.image_tensor = transforms.ToTensor()(img_copy)
  
        if self.current_display_mode is None:
            self.original_tensor = self.image_tensor.clone()
        
        return img_copy

    def reset(self):
        self.image_pil = None
        self.image_tensor = None
        self.original_tensor = None
        self.current_display_mode = None