# 尝试读取图片信息
from PIL import Image
import sys

# 图片路径
imgs = [
    r'media://inbound/e10a2cca-a329-474d-bbc0-a3705a2bd93e.jpg',
    r'media://inbound/6aa18e87-4298-4818-b423-200af7d72752.jpg'
]

for img_path in imgs:
    try:
        img = Image.open(img_path)
        print(f'图片: {img_path}')
        print(f'  大小: {img.size}')
        print(f'  模式: {img.mode}')
    except Exception as e:
        print(f'无法读取 {img_path}: {e}')
