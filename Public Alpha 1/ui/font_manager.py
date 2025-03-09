import os
from PyQt6.QtGui import QFontDatabase, QFont

class FontManager:
    @staticmethod
    def load_fonts():
        font_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts')
        available_fonts = []
        if os.path.exists(font_dir):
            for font_file in os.listdir(font_dir):
                if font_file.endswith('.ttf') or font_file.endswith('.otf'):
                    font_path = os.path.join(font_dir, font_file)
                    font_id = QFontDatabase.addApplicationFont(font_path)
                    if font_id != -1:
                        font_families = QFontDatabase.applicationFontFamilies(font_id)
                        available_fonts.extend(font_families)
        return available_fonts

    @staticmethod
    def get_font(font_name='default'):
        if font_name == 'default':
            return QFont()
        return QFont(font_name)

    @staticmethod
    def get_samsung_font():
        return "SamsungSans, sans-serif"

