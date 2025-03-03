class TextScaler:
    def __init__(self):
        self.base_width = 1280 
        self.base_height = 720  
        self.scale_factor = 1.0

    def update_scale_factor(self, width, height):
        width_scale = width / self.base_width
        height_scale = height / self.base_height
        self.scale_factor = min(width_scale, height_scale)
        return self.scale_factor

    def get_scaled_size(self, base_size):
        return int(base_size * self.scale_factor)

text_scaler = TextScaler()
