from PIL import Image
import pathlib

# 图片路径
imgs = [
    r'C:\Users\许耀仁\.openclaw\media\inbound\6aa18e87-4298-4818-b423-200af7d72752.jpg',
    r'C:\Users\许耀仁\.openclaw\media\inbound\e10a2cca-a329-474d-bbc0-a3705a2bd93e.jpg'
]

for img_path in imgs:
    img = Image.open(img_path)
    print(f"图片: {pathlib.Path(img_path).name}")
    print(f"  大小: {img.size[0]}x{img.size[1]}")
    print(f"  模式: {img.mode}")
    print(f"  格式: {img.format}")
    
    # 分析图片内容
    # 如果是截图，可能有大量空白区域
    import numpy as np
    arr = np.array(img)
    print(f"  数组形状: {arr.shape}")
    print(f"  平均亮度: {arr.mean():.1f}")
    
    # 检测是否可能是文字截图
    # 文字截图通常有高对比度
    if len(arr.shape) == 3:
        # 彩色图
        brightness = arr.mean(axis=2)
    else:
        brightness = arr
    
    high_contrast = (brightness.max() - brightness.min()) > 200
    print(f"  高对比度: {high_contrast} (可能是文字截图)")
    
    print()