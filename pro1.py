import os
import re
import pdfplumber
import pandas as pd
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


INVOICE_DIR = "invoices"
EXCEL_FILE = "extracted_data.xlsx"
CSV_FILE = "extracted_data.csv"
DB_FILE = "invoice_data.db"


os.makedirs(INVOICE_DIR, exist_ok=True)


REGEX_PATTERNS = {
    "Invoice Number": r"INVOICE[#\s:]*([A-Z]+\/[0-9]+)",            
    "Invoice Date": r"DATE\s+([A-Za-z]+\.\s+\d{1,2},\s+\d{4})",     
    "Amount": r"TOTAL\s+([0-9]+(?:\.\d{1,2})?)",                    
    "Vendor": r"(Mebigo Labs Private Limited)"                    
}

def extract_data_from_pdf(pdf_path):
    text = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'

    data = {}
    for field, pattern in REGEX_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        data[field] = match.group(1).strip() if match else "Not found"

    data["Filename"] = os.path.basename(pdf_path)
    return data


def process_all_pdfs():
    extracted_data = []
    for filename in os.listdir(INVOICE_DIR):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(INVOICE_DIR, filename)
            data = extract_data_from_pdf(filepath)
            extracted_data.append(data)
    return extracted_data

def save_to_excel_and_csv(data_list):
    df = pd.DataFrame(data_list)
    df.to_excel(EXCEL_FILE, index=False)
    df.to_csv(CSV_FILE, index=False)


def save_to_db(data_list):
    conn = sqlite3.connect(DB_FILE)
    df = pd.DataFrame(data_list)
    df.to_sql("invoices", conn, if_exists="append", index=False)
    conn.close()

class InvoiceApp:
    def __init__(self, root, data):
        self.root = root
        self.root.title("Invoice Tracker")
        self.data = data

        columns = ["Filename"] + list(REGEX_PATTERNS.keys())
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)
        self.tree.pack(fill=tk.BOTH, expand=True)

        for item in self.data:
            self.tree.insert("", tk.END, values=[item[col] for col in columns])

        frame = tk.Frame(root)
        frame.pack(pady=5)

        tk.Button(frame, text="Export to CSV and xlsx", command=self.export_excel_csv).pack(side=tk.LEFT, padx=10)
        tk.Button(frame, text="Export to DB", command=self.export_db).pack(side=tk.LEFT, padx=10)

    def export_excel_csv(self):
        save_to_excel_and_csv(self.data)
        messagebox.showinfo("Export", f"Saved to:\n- {EXCEL_FILE}\n- {CSV_FILE}")

    def export_db(self):
        save_to_db(self.data)
        messagebox.showinfo("Export", f"Data saved to database: {DB_FILE}")

if __name__ == "__main__":
    extracted_data = process_all_pdfs()
    print(f" Processed {len(extracted_data)} invoice(s) from '{INVOICE_DIR}'")

    root = tk.Tk()
    app = InvoiceApp(root, extracted_data)
    root.mainloop()
