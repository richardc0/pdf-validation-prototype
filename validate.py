"""
This script was used to create the figures for http://jrsmith3.github.io/sample-logs-the-secret-to-managing-multi-person-projects.html from a PDF file containing some old CMU sample logs.
"""
import PyPDF2
from polyglot.detect import Detector
from wand.color import Color
from wand.image import Image
import io


def pdf_page_to_png(src_pdf, pagenum = 0, resolution = 72,):
    """
    Returns specified PDF page as wand.image.Image png.

    :param PyPDF2.PdfFileReader src_pdf: PDF from which to take pages.
    :param int pagenum: Page number to take.
    :param int resolution: Resolution for resulting png in DPI.
    """
    dst_pdf = PyPDF2.PdfFileWriter()
    dst_pdf.addPage(src_pdf)

    pdf_bytes = io.BytesIO()
    dst_pdf.write(pdf_bytes)
    pdf_bytes.seek(0)

    img = Image(file=pdf_bytes, resolution=resolution)
    img.convert("png")

    return img


def validate_border(bg_img):
    with Color('white') as bg:
        with Image(width=793, height=1084, background=bg) as fg_img:
            bg_img.composite(fg_img, left=38, top=19)
            bg_img.save(filename='border_check.png')

            blob = bg_img.make_blob(format='RGB')

            # Iterate over blob and collect pixels
            for cursor in range(0, bg_img.width * bg_img.height * 3, 3):
                # Save tuple of color values
                if blob[cursor] < 255 or blob[cursor + 1] < 255 or blob[cursor + 2] < 255:
                    return False

    return True


def validate_content(text):
    for language in Detector(text).languages:
        print(language)


src_filename = "test-portrait.pdf"

src_pdf = PyPDF2.PdfFileReader(open(src_filename, "rb"))

page = src_pdf.getPage(0)

img = pdf_page_to_png(page)

page_content = page.extractText()
print(page_content.encode('utf-8'))

print(validate_border(img))

print(page.mediaBox)


