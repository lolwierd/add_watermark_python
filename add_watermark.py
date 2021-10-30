import os
import time
import sys
import logging
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def createwatermark(height, width):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.drawString(10, float(height)-10.0, "*SCANNED*")
    can.save()
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    return new_pdf


def add_watermark(filename, path):
    try:
        output = PdfFileWriter()
        # read your existing PDF
        print(f"'{filename}'")
        with open(rf"{path}", 'rb+') as pdf:
            existing_pdf = PdfFileReader(pdf)
            height = existing_pdf.getPage(0).mediaBox.upperLeft
            width = existing_pdf.getPage(0).mediaBox.lowerRight
            new_pdf = createwatermark(height=height[1], width=width[1])
            for pageNum in range(existing_pdf.numPages):
                pageObj = existing_pdf.getPage(pageNum)
                pageObj.mergePage(new_pdf.getPage(0))
                output.addPage(pageObj)
            pdf.seek(0)
            output.write(pdf)
            pdf.truncate()
            print("WATERMARKED PDF GENERATED.")

    except OSError:
        print("File is not accessible!")
        time.sleep(2)
        add_watermark(filename=filename, path=path)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s - %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1]
    filename, file_extension = os.path.splitext(path)
    add_watermark(filename, path)
