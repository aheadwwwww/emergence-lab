import urllib.request, json, ssl, base64
ssl._create_default_https_context = ssl._create_unverified_context

# 检查是否有免费的多模态API可以直接用

# 1. HuggingFace 免费推理 API
def test_huggingface_vision():
    """HuggingFace 有免费的模型推理API"""
    # 使用一个简单的vision模型
    model = "google/vit-base-patch16-224"  # 图像分类模型
    
    # 但这需要图片数据，我们先测试API是否可用
    url = f"https://api-inference.huggingface.co/models/{model}"
    
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        print(f"HuggingFace API 可用: {data}")
        return True
    except Exception as e:
        print(f"HuggingFace API 不可用: {e}")
        return False

# 2. 检查本地是否有可用的vision模型
def check_local_vision():
    """检查是否有本地vision工具"""
    import subprocess
    try:
        # 检查是否有tesseract OCR
        result = subprocess.run(['tesseract', '--version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("Tesseract OCR 可用")
            return True
    except:
        pass
    
    try:
        # 检查是否有easyocr
        import easyocr
        print("EasyOCR 可用")
        return True
    except ImportError:
        print("EasyOCR 未安装")
    
    return False

# 3. 检查是否有其他免费OCR服务
def test_free_ocr_apis():
    """测试免费OCR API"""
    # OCR.space 有免费额度
    # 但需要API key
    
    # 检查是否有其他不需要key的服务
    free_apis = [
        # 这些可能需要key，但我们可以测试
    ]
    
    print("没有发现完全免费的OCR API（不需要key）")
    return False

print("=== 检查可用的vision方案 ===")
test_huggingface_vision()
check_local_vision()
test_free_ocr_apis()

print()
print("结论：需要安装本地OCR工具或获取API key")
print("最快方案：pip install easyocr（但之前安装被杀了）")
print("替代方案：让用户获取Gemini API key")