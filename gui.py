import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from banks import Bank

class SGBankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Converter")
        self.parts = []
        self.final_array = []
        self.input_file_path = tk.StringVar()
        self.type_of_file = tk.StringVar()
        self.year = tk.StringVar()

        self.create_widgets()

    def get_all_file_types(self, parent_class):
        subclasses = []
        for sc in parent_class.__subclasses__():
            subclasses.append(sc.get_type())
            subclasses.extend(self.get_all_file_types(sc))
        return subclasses
    
    def is_csv_file(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        return file_extension.lower() == ".csv"
    
    def is_pdf_file(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        return file_extension.lower() == ".pdf"
    
    def visitor_body(self, text, cm, tm, fontDict, fontSize):
        self.parts.extend(text.split('\n'))
    
    def create_widgets(self):
        # Input CSV File
        tk.Label(self.root, text="Input CSV File:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(self.root, textvariable=self.input_file_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_input_file).grid(row=0, column=2, padx=5, pady=5)

        # Type of File ComboBox
        file_types = self.get_all_file_types(Bank)
        self.type_of_file = tk.StringVar()
        self.type_of_file.set(file_types[0])  # Set the default value
        tk.Label(self.root, text="Type of File:").grid(row=1, column=0, padx=5, pady=5)
        combo_box = ttk.Combobox(self.root, textvariable=self.type_of_file, values=file_types, width=47)
        combo_box.grid(row=1, column=1, padx=10, pady=10)

        # Year Input
        tk.Label(self.root, text="Year:").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(self.root, textvariable=self.year, width=50).grid(row=2, column=1, padx=5, pady=5)

        # Convert Button
        tk.Button(self.root, text="Convert", command=self.convert_file).grid(row=3, column=1, padx=5, pady=5)


    def browse_input_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("PDF files", "*.pdf")])
        if file_path:
            self.input_file_path.set(file_path)

            
    def convert_file(self):
        input_file = self.input_file_path.get()
        type_of_file = self.type_of_file.get()

        if not input_file:
            tk.messagebox.showerror("Error", "Please select an input CSV/PDF file.")
            return

        try:
            instance = Bank.create_instance_from_type_string(type_of_file, self.year.get())
            instance.parse(input_file)
            tk.messagebox.showinfo("Success", "CSV file converted successfully!")
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    
if __name__ == "__main__":
    root = tk.Tk()
    app = SGBankApp(root)
    root.mainloop()

