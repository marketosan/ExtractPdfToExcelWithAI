import json
import re
from pathlib import Path

import ollama
import pdfplumber

from pdf_extractor import PdfExtractor
from product import Product


class AiPdfExtractor(PdfExtractor):
    REQUEST_TEMPLATE_PATH = Path(__file__).parent / "ai_request_message_template.txt"
    PDF_TEXT_PLACEHOLDER = "[PDF_RECEIPT_PLACEHOLDER]"
    CONTEXT_SIZE = 16384
    TEMPERATURE = 0

    def __init__(self, file_paths_set, ai_model):
        super().__init__(file_paths_set)
        self.ai_model = ai_model
        self.request_template = self.REQUEST_TEMPLATE_PATH.read_text(encoding="utf-8")

    def before_extraction(self):
        # Load the model once and keep it in memory for all the PDFs
        ollama.generate(model=self.ai_model.model_name, keep_alive=-1)

    def extract_file(self, file_path):
        with pdfplumber.open(file_path) as pdf:
            # New line between pages, so the last line of a page is not merged with the next one
            rearranged_pdf_text = '\n'.join(page.extract_text(x_tolerance_ratio=0.15) for page in pdf.pages)

        # Keep only the PO number line and the product lines (start with a 5-digit item number),
        # so the  model is not confused by DWG notes, page headers and terms
        lines = rearranged_pdf_text.splitlines()
        po_line = next((line for line in lines if line.startswith('PURCHASE ORDER:')), '')
        product_lines = [line for line in lines if re.match(r'^\d{5} ', line)]
        rearranged_pdf_text = '\n'.join([po_line] + product_lines)

        # add the inmportant info from the pdf in a template which would be asking the AI model to read this content and get needed info
        request_message = self.request_template.replace(self.PDF_TEXT_PLACEHOLDER, rearranged_pdf_text)

        # Each PDF is a separate chat, same num_ctx so the model is not reloaded
        response = ollama.chat(
            model=self.ai_model.model_name,
            messages=[
                {'role': 'user', 'content': request_message}
            ],
            format="json",
            options={"num_ctx": self.CONTEXT_SIZE, "temperature": self.TEMPERATURE},
            keep_alive=-1
        )

        ai_response = json.loads(response.message.content)
        # Handle JSON that was encoded twice
        if isinstance(ai_response, str):
            ai_response = json.loads(ai_response)

        for item in ai_response.get("products", []):
            self.extracted_products.append(Product(
                item.get("part_number"),
                item.get("description"),
                int(item.get("quantity")),
                item.get("delivery_date"),
                str(item.get("purchase_order")),
            ))

    def after_extraction(self):
        # Unload the model when all PDFs are done
        ollama.generate(model=self.ai_model.model_name, keep_alive=0)