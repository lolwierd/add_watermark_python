import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
import socket

import win32serviceutil

import servicemanager
import win32event
import win32service


class SMWinservice(win32serviceutil.ServiceFramework):
    '''Base class to create winservice in Python'''

    _svc_name_ = 'PDF Watermarker'
    _svc_display_name_ = 'Python Service to Watermark PDFs'
    _svc_description_ = 'Python Service to Watermark PDFs'

    @classmethod
    def parse_command_line(cls):
        '''
        ClassMethod to parse the command line
        '''
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        '''
        Constructor of the winservice
        '''
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        '''
        Called when the service is asked to stop
        '''
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        '''
        Called when the service is asked to start
        '''
        self.start()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def start(self):
        '''
        Override to add logic before the start
        eg. running condition
        '''
        pass

    def stop(self):
        '''
        Override to add logic before the stop
        eg. invalidating running condition
        '''
        pass

    def main(self):
        '''
        Main class to be ovverridden to add logic
        '''
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        path = os.getenv("USERPROFILE")+"\Desktop\Scanned"
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


def createwatermark(height, width):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.drawString(10, float(height)-10.0, "*SCANNED*")
    can.save()
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    return new_pdf


def add_watermark(filename, path):
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
    SMWinservice.parse_command_line()
