import io

import PyPDF2
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A3, A4
from PyPDF2 import PdfFileReader, PdfFileWriter
from PIL import Image


def png_from_pdf(pdf_endpoint, page_number):

    output = BytesIO()

    with Image(blob=pdf_endpoint.get_data(), resolution=150) as pdf:
        with Image(width=pdf.width, height=pdf.height) as image:
            try:
                page = pdf.sequence[page_number - 1]
            except IndexError:
                abort(400, 'Letter does not have a page {}'.format(page_number))

            image.composite(page, top=0, left=0)
            converted = image.convert('png')
            converted.save(file=output)

    output.seek(0)

    return {
        'filename_or_fp': output,
        'mimetype': 'image/png',
    }



# Check for a border
def is_there_a_border(im):
    from PIL import Image
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    from PIL import ImageChops
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    return bbox != (0, 0, im.size[0], im.size[1])


# read your existing PDF
existing_pdf = PdfFileReader(open("test.pdf", "rb"))

pdf_info = existing_pdf.getDocumentInfo()
print(str(pdf_info))

output = PdfFileWriter()
# add the "watermark" (which is the new pdf) on the existing page
page = existing_pdf.getPage(0)

pdf_page_to_png(existing_pdf)

page_content = page.extractText()
print(page_content.encode('utf-8'))

rotation = page.get('/Rotate')
print(page.mediaBox)
print("rotate: " + str(rotation))

portrait = True

if rotation:
    if (rotation / 180) > 0:
        print("landscape")
        portrait = False
    else:
        print("portrait")

packet = io.BytesIO()
# create a new PDF with Reportlab
can = canvas.Canvas(packet, pagesize=A4)

pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
can.setFont('Arial', 6)
can.drawString(2, float(page.mediaBox[3])-float(2), "NOTIFY")
can.save()

# move to the beginning of the StringIO buffer
packet.seek(0)
new_pdf = PdfFileReader(packet)

page.mergePage(new_pdf.getPage(0))
output.addPage(page)
# finally, write "output" to a real file
outputStream = open("destination.pdf", "wb")
output.write(outputStream)
outputStream.close()
