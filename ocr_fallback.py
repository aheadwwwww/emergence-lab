"""
简单的图片文字识别方案

如果easyocr安装失败，我们可以：
1. 用Pillow读取图片基本信息
2. 用现有的免费工具（如果机器上有）
"""

from PIL import Image
import subprocess
import sys
import pathlib

def extract_text_from_image(image_path):
    """
    尝试多种方法提取图片文字
    """
    methods = []
    
    # 方法1：如果有tesseract
    try:
        result = subprocess.run(
            ['tesseract', image_path, 'stdout'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            methods.append(('tesseract', result.stdout))
    except:
        pass
    
    # 方法2：如果有easyocr
    try:
        import easyocr
        reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
        result = reader.readtext(image_path)
        text = ' '.join([r[1] for r in result])
        if text:
            methods.append(('easyocr', text))
    except:
        pass
    
    # 方法3：如果有pytesseract
    try:
        import pytesseract
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        if text.strip():
            methods.append(('pytesseract', text))
    except:
        pass
    
    # 方法4：调用在线OCR服务（如果有API key）
    # 暂时跳过
    
    if methods:
        return methods[0][1]  # 返回第一个成功的结果
    else:
        return None

# 测试图片路径
def test_with_sample():
    """测试是否有可用的图片"""
    # 查找workspace里的图片
    workspace = pathlib.Path.home() / '.openclaw' / 'workspace'
    images = list(workspace.rglob('*.png')) + list(workspace.rglob('*.jpg'))
    
    if images:
        print(f"找到 {len(images)} 个图片")
        for img in images[:3]:
            print(f"  {img.name}")
            text = extract_text_from_image(str(img))
            if text:
                print(f"  内容: {text[:100]}...")
            else:
                print(f"  无法提取文字（没有OCR工具）")
    else:
        print("没有找到测试图片")

if __name__ == '__main__':
    print("检查可用的OCR方法...")
    test_with_sample()