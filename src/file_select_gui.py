import tkinter as tk
from datetime import datetime
from tkinter import filedialog

from extraction_approach import ExtractionApproach


class FileSelectGUI:
    FRAME_WIDTH = 450
    DISTANCE_FROM_TOP = 700
    DISTANCE_FROM_LEFT = 1200
    RESIZABLE_X = False
    RESIZABLE_Y = False

    RESULT_FILE_PREFIX = "extracted_pdfs-"
    DATE_TIME_FORMAT = "%d_%b_%Y-%H_%M_%S"

    EXTRACTION_APPROACH_TITLE = "Extraction Approach"
    DEFAULT_EXTRACTION_APPROACH = ExtractionApproach.RULE_BASED
    APPROACH_MARGIN_TOP = 15
    APPROACH_MARGIN_BOTTOM = 10


    def __init__(self):
        self.root_frame = tk.Tk()
        self.root_frame.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.file_paths_to_extract = set()
        self.extracted_file_name_with_path = None
        self.extraction_approach = None

        # Configure window properties
        self.root_frame.title("Extract PDF to Excel")
        self.root_frame.resizable(self.RESIZABLE_X, self.RESIZABLE_Y)

        # Create listbox to display file paths
        self.listbox = tk.Listbox(self.root_frame, width=70, height=14)
        self.listbox.pack(pady=10)

        # Create frame for buttons
        self.button_frame = tk.Frame(self.root_frame)
        self.button_frame.pack()

        # Create "Browse" button
        self.browse_button = tk.Button(self.button_frame, text="Select Files", command=self.browse_files, width=10)
        self.browse_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Create "Save" button
        self.extract_button = tk.Button(self.button_frame, text="Extract", command=self.extract_paths, width=10)
        self.extract_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Create radio buttons to select the extraction approach
        self.approach_frame = tk.LabelFrame(self.root_frame, text=self.EXTRACTION_APPROACH_TITLE)
        self.approach_frame.pack(pady=(self.APPROACH_MARGIN_TOP, self.APPROACH_MARGIN_BOTTOM))
        self.approach_var = tk.StringVar(value=self.DEFAULT_EXTRACTION_APPROACH.name)
        for approach in ExtractionApproach:
            tk.Radiobutton(self.approach_frame, text=approach.label, variable=self.approach_var,
                           value=approach.name).pack(side=tk.LEFT, padx=5)

        # Fit the window height to its content, so there is no empty space at the bottom
        self.root_frame.update_idletasks()
        self.root_frame.geometry(f"{self.FRAME_WIDTH}x{self.root_frame.winfo_reqheight()}"
                                 f"+{self.DISTANCE_FROM_LEFT}+{self.DISTANCE_FROM_TOP}")

        self.root_frame.mainloop()

    def on_closing(self):
        self.root_frame.destroy()
        exit()

    def browse_files(self):
        # open dialog to select files that allows to select only pdf files
        selected_files = set(filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf *.PDF")]))
        for file_path in selected_files:
            file_name = file_path.strip().split('/')[-1]
            self.listbox.insert(tk.END, file_name)
            self.file_paths_to_extract.add(file_path)

    def extract_paths(self):
        if not self.file_paths_to_extract:
            return

        self.extracted_file_name_with_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=self.get_file_name()
        )

        if not self.extracted_file_name_with_path:
            return

        self.extraction_approach = ExtractionApproach[self.approach_var.get()]
        self.root_frame.quit()


    def get_file_name(self):
        current_date_time = datetime.now()
        formatted_date_time = current_date_time.strftime(self.DATE_TIME_FORMAT)
        return self.RESULT_FILE_PREFIX + formatted_date_time + ".xlsx"


# if __name__ == "__main__":
#     app = FileSelectGUI()
#
#     # After the GUI is closed, you can access the selected file paths
#     selected_paths = app.file_paths_to_extract
#     if app.extracted_file_name_with_path:
#         print(" File save to: " + app.extracted_file_name_with_path)
#         print("Extraction approach: " + app.extraction_approach.label)
#     print("Selected paths:")
#     for path in selected_paths:
#         print(path)
