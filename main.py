import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
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
        with open(rf"{path}", 'rb') as pdf:
            existing_pdf = PdfFileReader(pdf)
            height = existing_pdf.getPage(0).mediaBox.upperLeft
            width = existing_pdf.getPage(0).mediaBox.lowerRight
            new_pdf = createwatermark(height=height[1], width=width[1])
            for pageNum in range(existing_pdf.numPages):
                pageObj = existing_pdf.getPage(pageNum)
                pageObj.mergePage(new_pdf.getPage(0))
                output.addPage(pageObj)

            outputStream = open(filename+"__watermarked.pdf", "wb")
            output.write(outputStream)
            outputStream.close()
            print("WATERMARKED PDF GENERATED.")
    except OSError:
        print("OS ERROR AAYA")
        add_watermark(filename=filename, path=path)


class CustomHandler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        path = event.src_path
        if event.is_directory:
            return None
        elif "__watermarked" in path:
            return None

        elif event.event_type == 'created':
            filename, file_extension = os.path.splitext(path)
            if file_extension == ".pdf":
                print("Watchdog received created event - % s" %
                      filename)
                time.sleep(5)
                add_watermark(filename, path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = os.getenv("USERPROFILE")+"\Documents\Scanned"
    event_handler = CustomHandler()
    observer = Observer()
    observer.schedule(event_handler, path)
    observer.start()
    print("INITIALIZED SERVICE WAITING FOR SCANNED PDFS.")
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
