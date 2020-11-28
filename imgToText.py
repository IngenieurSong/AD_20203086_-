from PIL import Image
import pytesseract
from gtts import gTTS
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

class Ocr:

    def __init__(self, fname):
        self.image_file = fname
        self.img = Image.open(self.image_file)
        self.textResult = ''

    def ocr_tesseract(self):
        self.textResult = pytesseract.image_to_string(self.img, lang='eng+kor')
        self.img.close()

    def textToSpeech(self):
        tts = gTTS(text=self.textResult, lang='ko')
        tts.save('%s.wav' %self.image_file)