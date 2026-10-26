import traceback
from abc import ABC, abstractmethod

import tkinter as tk
from tkinter import messagebox


class PdfExtractor(ABC):
    """Base class for the extraction approaches. Subclasses only implement how one file is extracted."""

    def __init__(self, file_paths_set):
        if isinstance(file_paths_set, set) or isinstance(file_paths_set, list):
            self.file_paths_set = file_paths_set
        else:
            self.file_paths_set = {file_paths_set}

        self.extracted_products = list()

    def extract_files(self):
        # e.g. when Ollama is not running for the AI approach
        try:
            self.before_extraction()
        except Exception as e:
            self.show_error_popup(e)
            print(e)
            exit()

        try:
            for file_path in self.file_paths_set:
                try:
                    self.extract_file(file_path)
                except Exception as e:
                    self.show_error_popup(e, file_path)
                    print(e)
                    exit()
        finally:
            self.after_extraction()
        print("Received data successfully")

    @abstractmethod
    def extract_file(self, file_path):
        """Extract the products of one file and add them to self.extracted_products"""

    def before_extraction(self):
        """Optional hook that runs once before all files are extracted"""

    def after_extraction(self):
        """Optional hook that runs once after all files are extracted, also on error"""

    def print_extracted_data(self):
        for item in self.extracted_products:
            print(item)
            print('-----------------')

    @staticmethod
    def show_error_popup(exception, file=None):
        title = "Error on file: " + file.strip().split('/')[-1] if file else "Error before extraction"
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        error_message = f"{type(exception).__name__}: {str(exception)}\n Please contact admin to resolve issue.\n\nTraceback:\n{traceback.format_exc()}"
        messagebox.showerror(title, error_message)