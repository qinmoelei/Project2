from fpdf import FPDF
from original_text import text1


class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        pass


def trasnform_text_pdf(text,pdf_output_path):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)

    pdf.multi_cell(0, 10, text.encode("latin-1", "replace").decode("latin-1"))
    pdf.output(name=pdf_output_path)
    pdf_output_path


if __name__ == "__main__":
    # Create a PDF object and set properties
    pdf = PDF()
    pdf.add_page()
    
    # Chinese text
    chinese_text = text1

    # Add text
    pdf.multi_cell(0, 10, chinese_text.encode("latin-1", "replace").decode("latin-1"))

    # Save the PDF
    pdf_output_path = "save_pdf/original_text.pdf"
    pdf.output(name=pdf_output_path)

    pdf_output_path
