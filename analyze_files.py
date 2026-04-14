import PyPDF2
import pandas as pd
import json

def extract_pdf_text(filepath):
    text = ""
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        text = f"Error reading {filepath}: {e}"
    return text

with open("output.txt", "w", encoding="utf-8") as out_f:
    out_f.write("--- 1.WEB SCRAPING_BASE.pdf ---\n")
    scraping_text = extract_pdf_text("1.WEB SCRAPING_BASE.pdf")
    out_f.write(scraping_text[:3000] + "\n")

    out_f.write("\n--- 1.Censo Digital de Ferreterías en Colombia.pptx.pdf ---\n")
    censo_text = extract_pdf_text("1.Censo Digital de Ferreterías en Colombia.pptx.pdf")
    out_f.write(censo_text[:3000] + "\n")

    out_f.write("\n--- Bd_Base.xlsx ---\n")
    try:
        df = pd.read_excel("Bd_Base.xlsx")
        out_f.write(f"Columns: {list(df.columns)}\n")
        out_f.write(f"Shape: {df.shape}\n")
        out_f.write("Data sample:\n")
        out_f.write(df.head(5).to_markdown() + "\n")
    except Exception as e:
        out_f.write(f"Error reading Bd_Base.xlsx: {e}\n")
