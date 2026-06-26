import PyPDF2

pdf_path = r'C:\Users\许耀仁\.openclaw\media\inbound\工作操作系统_3---724e4e6b-2b0e-40b2-a2e3-302fe1ae2906.pdf'

with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    print(f"页数: {len(reader.pages)}")
    
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    print(text[:5000])