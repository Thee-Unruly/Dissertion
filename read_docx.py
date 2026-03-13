from docx import Document
import os

def read_docx(file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return
    doc = Document(file_path)
    for para in doc.paragraphs:
        print(para.text)

if __name__ == "__main__":
    read_docx("c:\\Users\\ibrahim.fadhili\\OneDrive - Agile Business Solutions\\Desktop\\Dissertion\\Offensive_Module_Implementation_Detailed.docx")
