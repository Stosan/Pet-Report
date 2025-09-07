# pdf_generator_pet.py
# --- VERSION 1.1.35 - ADD FULL PAGE SECTION IMAGES ---
# --- VERSION 1.1.34 - PATCH 22: Forceful Canvas Reset for Cover Duplication ---
# --- VERSION 1.1.34 - PATCH 21: Aggressive Cover Page Duplication Debug ---
# --- VERSION 1.1.34 - PATCH 20: Debugging Cover Page Duplication & Canvas Clear ---
# ... (previous version history)

import os
import random
import logging
import json
import sys
import re
from reportlab.pdfgen import canvas


# --- ReportLab Imports ---
try:
    from reportlab.lib.styles import ParagraphStyle, StyleSheet1
    from reportlab.lib.colors import HexColor, black, white, Color, magenta, lightgrey, navy, red
    from reportlab.lib import colors # Ensure colors is imported directly
    from reportlab.platypus import (
        Paragraph, Spacer, Image, PageBreak, Table, TableStyle,
        KeepInFrame, NextPageTemplate, Flowable
    )
    from reportlab.platypus.flowables import KeepInFrame as ReportLabKeepInFrame
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.utils import ImageReader
    from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate, Frame
    from reportlab.lib.pagesizes import letter
    reportlab_available = True
    _StyleSheetClass = StyleSheet1
    _ParaStyleClass = ParagraphStyle
    _HexColorFunc = HexColor
    _ColorClass = Color

    TA_LEFT = TA_LEFT
    TA_CENTER = TA_CENTER
    TA_RIGHT = TA_RIGHT
    TA_JUSTIFY = TA_JUSTIFY
    inch = inch

except ImportError as e:
    reportlab_available = False
    logging.critical(f"ReportLab components not found: {e}. PDF generation will fail.")
    # Dummy classes/functions
    class StyleSheet1:
        def __init__(self): self._styles = {}
        def add(self, style, alias=None): self._styles[style.name] = style; self._styles[alias or style.name] = style
        def __getitem__(self, key): return self._styles.get(key)
        def get(self, key, default=None): return self._styles.get(key, default)
    class ParagraphStyle:
        def __init__(self, name, **kwargs): self.name = name; self.__dict__.update(kwargs)
    def HexColor(val): return val
    class Color:
        def __init__(self, r, g, b, alpha=1): self.r=r; self.g=g; self.b=b; self.alpha=alpha
        def __str__(self): return f"Color({self.r},{self.g},{self.b})"

    white = Color(1,1,1)
    magenta = Color(1,0,1)
    lightgrey = Color(0.827,0.827,0.827)
    navy = Color(0,0,0.5)
    red = Color(1,0,0)

    class Paragraph:
        def __init__(self, text, style): self.text = text; self.style = style
        def wrap(self, availWidth, availHeight):
            if not hasattr(self, 'style') or not hasattr(self.style, 'fontSize'): return (availWidth, 15)
            lines = self.text.count('<br/>') + self.text.count('\n') + 1
            height = lines * (self.style.fontSize * 1.2 if self.style.fontSize else 15)
            return (min(availWidth, len(self.text) * (self.style.fontSize*0.6 if self.style.fontSize else 10)), height)
        def drawOn(self, canv, x, y, _sW=0): pass
    class Spacer:
        def __init__(self, width, height): self.width = width; self.height = height
    class Image:
        def __init__(self, filename, width=None, height=None):
            self.filename=filename; self.imageWidth=width or 100; self.imageHeight=height or 100
            self.drawWidth=width or 100; self.drawHeight=height or 100
        def wrapOn(self, canv, availWidth, availHeight): return self.drawWidth, self.drawHeight
        def drawOn(self, canv, x, y, _sW=0): pass
    class PageBreak: pass
    class NextPageTemplate:
        def __init__(self, template_name): self.template_name = template_name
    class Table:
        def __init__(self, data, colWidths=None, rowHeights=None, style=None, **kwargs): pass
    class TableStyle:
        def __init__(self, cmds=None, **kwargs): pass


    inch_dummy=72;
    TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY = 0,1,2,4
    inch = inch_dummy if 'inch' not in globals() else inch
    _StyleSheetClass = StyleSheet1
    _ParaStyleClass = ParagraphStyle
    _HexColorFunc = HexColor
    ImageReader = None
    if 'colors' not in globals():
        class DummyColorsModule:
            Color = Color
            white = white
            HexColor = HexColor
            lightgrey = lightgrey
        colors = DummyColorsModule()


# --- Additional Imports for AI Pet Portrait Feature & Font Handling ---
import requests
import uuid
import math # <<< NEW CODE START >>> For page number calculation <<< NEW CODE END >>>

# --- Path Definitions ---
try:
    SCRIPT_DIR_PET = os.path.dirname(os.path.realpath(__file__))
except NameError:
    SCRIPT_DIR_PET = os.getcwd()
PROJECT_ROOT_PET = os.path.abspath(os.path.join(SCRIPT_DIR_PET, os.pardir))
ASSETS_DIR_PET = os.path.join(SCRIPT_DIR_PET, 'assets')
FONTS_DIR_PET = os.path.join(ASSETS_DIR_PET, 'fonts')
COMMON_DATA_JSONS_DIR_PET = os.path.join(PROJECT_ROOT_PET, 'common', 'Data jsons')
if not os.path.isdir(COMMON_DATA_JSONS_DIR_PET):
    DATA_JSONS_DIR_PET = os.path.join(SCRIPT_DIR_PET, 'Data jsons')
    os.makedirs(DATA_JSONS_DIR_PET, exist_ok=True)
else:
    DATA_JSONS_DIR_PET = COMMON_DATA_JSONS_DIR_PET

def _clean_mika_voice(text: str) -> str:
    if not isinstance(text, str): return text
    return re.sub(r"\s*\(\s*(?:Mika['’]s Voice:|Reminder: This is a loving tribute for.*?|This section is part of a loving memorial for.*?|Instruction to AI:.*?|Note to AI:.*?)[^)]*\)\s*", "", text, flags=re.IGNORECASE | re.DOTALL).strip()

# --- Logger Setup ---
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    log_formatter_pet = logging.Formatter('%(asctime)s - %(levelname)s - PET_PDFGEN:%(lineno)d - %(message)s')
    log_handler_pet = logging.StreamHandler(sys.stdout); log_handler_pet.setFormatter(log_formatter_pet); logger.addHandler(log_handler_pet)
    logger.setLevel(logging.DEBUG); logger.info("Pet PDF Generator Logger configured (DEBUG LEVEL).")

# --- Styling Constants ---
COLOR_PAGE_BACKGROUND = _HexColorFunc('#F5F0E1') if reportlab_available else Color(0.96, 0.94, 0.88) #F5F0E1
COLOR_HEADER_TEAL = _HexColorFunc('#3A7E7E') if reportlab_available else Color(0.23, 0.49, 0.49) #3A7E7E
COLOR_BODY_TEXT_DARK = _HexColorFunc('#333333') if reportlab_available else Color(0.2, 0.2, 0.2) #333333
COLOR_FOOTER_TEXT = _HexColorFunc('#777777') if reportlab_available else Color(0.47, 0.47, 0.47) #777777


# --- Font Configuration ---
FALLBACK_FONT_SANS = "Helvetica"
FALLBACK_FONT_SANS_ITALIC = "Helvetica-Oblique"
FALLBACK_FONT_SANS_BOLD = "Helvetica-Bold"
FALLBACK_FONT_SERIF_BOLD = "Times-Bold"

REGISTERED_DEJAVU_FONT = FALLBACK_FONT_SANS
REGISTERED_DEJAVU_FONT_BOLD = FALLBACK_FONT_SANS_BOLD


# --- Custom Canvas ---
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        self.client_name_for_footer = kwargs.pop('client_name_for_footer', "Valued Client")
        # self.page_number_offset = kwargs.pop('page_number_offset', 0) # MODIFIED LINE: This specific offset is no longer used directly for logical page number calculation in footer
        super().__init__(*args, **kwargs)

# --- BasePDFBuilder ---
class BasePDFBuilder:
    def __init__(self, output_path, generation_context):
        self.output_path = output_path
        self.generation_context = generation_context
        self.client_name = generation_context.get('client_name', 'Valued Client')
        self.logger = logging.getLogger(__name__)

        self.assets_dir = generation_context.get('assets_dir', ASSETS_DIR_PET)
        self.fonts_dir_from_context = generation_context.get('fonts_dir', FONTS_DIR_PET)
        self.data_jsons_dir = generation_context.get('data_jsons_dir', DATA_JSONS_DIR_PET)
        self.images_dir = os.path.join(self.assets_dir, 'images')

        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(os.path.join(self.images_dir, "covers"), exist_ok=True)
        os.makedirs(os.path.join(self.images_dir, "dividers"), exist_ok=True)
        os.makedirs(self.fonts_dir_from_context, exist_ok=True)
        self.dejavu_fonts_dir = os.path.join(PROJECT_ROOT_PET, "common", "fonts")
        os.makedirs(self.dejavu_fonts_dir, exist_ok=True)


        self._register_fonts_and_set_default()

        self.sans_italic_font = FALLBACK_FONT_SANS_ITALIC
        self.serif_font = 'Times-Roman'
        self.serif_bold_font = FALLBACK_FONT_SERIF_BOLD

        self.occasion_style_config = {}
        occasion_styles_path = os.path.join(self.data_jsons_dir, 'pet_occasion_styles.json')
        if not os.path.exists(occasion_styles_path):
            occasion_styles_path = os.path.join(self.data_jsons_dir, 'occasion_styles.json')
        if os.path.exists(occasion_styles_path):
            try:
                with open(occasion_styles_path, 'r', encoding='utf-8') as f: self.occasion_style_config = json.load(f)
            except Exception as e: self.logger.error(f"Error loading styles from {occasion_styles_path}: {e}")
        else:
            self.logger.warning(f"Styles file {occasion_styles_path} not found.")

        self.styles = self._create_styles()

    def _register_fonts_and_set_default(self):
        global REGISTERED_DEJAVU_FONT, REGISTERED_DEJAVU_FONT_BOLD
        if not reportlab_available or not hasattr(pdfmetrics, 'registerFont') or not TTFont:
            self.logger.warning("ReportLab pdfmetrics or TTFont not available. Font registration skipped.")
            self.sans_font = FALLBACK_FONT_SANS; self.sans_bold_font = FALLBACK_FONT_SANS_BOLD
            REGISTERED_DEJAVU_FONT = FALLBACK_FONT_SANS; REGISTERED_DEJAVU_FONT_BOLD = FALLBACK_FONT_SANS_BOLD
            return

        self.logger.info(f"Attempting to load DejaVu fonts from: {self.dejavu_fonts_dir}")

        dejavu_regular_path = os.path.join(self.dejavu_fonts_dir, "DejaVuSans.ttf")
        dejavu_bold_path = os.path.join(self.dejavu_fonts_dir, "DejaVuSans-Bold.ttf")

        if os.path.exists(dejavu_regular_path):
            try:
                pdfmetrics.registerFont(TTFont("DejaVu", dejavu_regular_path))
                self.sans_font = "DejaVu"; REGISTERED_DEJAVU_FONT = "DejaVu"
                self.logger.info(f"Successfully registered font 'DejaVu' from {dejavu_regular_path}.")
            except Exception as e:
                self.logger.error(f"Failed to register 'DejaVu' from {dejavu_regular_path}: {e}. Using fallback.")
                self.sans_font = FALLBACK_FONT_SANS; REGISTERED_DEJAVU_FONT = FALLBACK_FONT_SANS
        else:
            self.logger.warning(f"DejaVuSans.ttf not found in {self.dejavu_fonts_dir}. Using fallback {FALLBACK_FONT_SANS}.")
            self.sans_font = FALLBACK_FONT_SANS; REGISTERED_DEJAVU_FONT = FALLBACK_FONT_SANS

        if os.path.exists(dejavu_bold_path):
            try:
                pdfmetrics.registerFont(TTFont("DejaVu-Bold", dejavu_bold_path))
                self.sans_bold_font = "DejaVu-Bold"; REGISTERED_DEJAVU_FONT_BOLD = "DejaVu-Bold"
                self.logger.info(f"Successfully registered font 'DejaVu-Bold' from {dejavu_bold_path}.")
            except Exception as e:
                self.logger.error(f"Failed to register 'DejaVu-Bold' from {dejavu_bold_path}: {e}. Using fallback.")
                self.sans_bold_font = FALLBACK_FONT_SANS_BOLD; REGISTERED_DEJAVU_FONT_BOLD = FALLBACK_FONT_SANS_BOLD
        else:
            self.logger.warning(f"DejaVuSans-Bold.ttf not found in {self.dejavu_fonts_dir}. Using fallback {FALLBACK_FONT_SANS_BOLD}.")
            self.sans_bold_font = FALLBACK_FONT_SANS_BOLD; REGISTERED_DEJAVU_FONT_BOLD = FALLBACK_FONT_SANS_BOLD

        self.logger.info(f"Font registration. Sans: '{self.sans_font}', Bold Sans: '{self.sans_bold_font}'. All Registered: {pdfmetrics.getRegisteredFontNames()}")

    def _create_styles(self):
        styles = _StyleSheetClass() if _StyleSheetClass else StyleSheet1()
        std_font = self.sans_font
        std_bold_font = self.sans_bold_font
        std_italic_font = self.sans_italic_font
        serif_bold_font_main = self.serif_bold_font

        styles.add(_ParaStyleClass(name='BodyText', fontName=std_font, fontSize=12, leading=12*1.5, alignment=TA_LEFT, textColor=COLOR_BODY_TEXT_DARK, spaceAfter=0.2*inch))
        styles.add(_ParaStyleClass(name='Normal', parent=styles['BodyText']))
        styles.add(_ParaStyleClass(name='TOCReportHeader', fontName=std_bold_font, fontSize=34, alignment=TA_CENTER, textColor=COLOR_HEADER_TEAL, spaceBefore=0.3*inch, spaceAfter=0.6*inch))
        styles.add(_ParaStyleClass(name='TOCEntryStyle', parent=styles['Normal'], fontName=std_font, leftIndent=0.2*inch, fontSize=15, leading=15*1.6, spaceBefore=6, spaceAfter=10))
        styles.add(_ParaStyleClass(name='SectionTitle', fontName=std_bold_font, fontSize=30, leading=30*1.2, alignment=TA_CENTER, textColor=COLOR_HEADER_TEAL, spaceBefore=0.2*inch, spaceAfter=0.2*inch))
        styles.add(_ParaStyleClass(name='H1Style', fontName=std_bold_font, fontSize=22, leading=22*1.3, alignment=TA_LEFT, textColor=COLOR_HEADER_TEAL, spaceBefore=0.4*inch, spaceAfter=0.2*inch))
        styles.add(_ParaStyleClass(name='ReportMainTitle', parent=styles['SectionTitle'], fontName=std_bold_font, fontSize=36, alignment=TA_CENTER, spaceAfter=0.1*inch, leading=36*1.25))
        styles.add(_ParaStyleClass(name='ReportSubTitle', parent=styles['Normal'], fontName=std_font, fontSize=18, alignment=TA_CENTER, textColor=COLOR_BODY_TEXT_DARK, spaceAfter=0.3*inch, leading=18*1.35))
        styles.add(_ParaStyleClass(name='PetQuoteStyle', fontName=std_italic_font, fontSize=11.5, leading=11.5*1.5, textColor=COLOR_BODY_TEXT_DARK, alignment=TA_LEFT, leftIndent=0.5*inch, rightIndent=0.5*inch, spaceBefore=0.3*inch, spaceAfter=0.3*inch))
        styles.add(_ParaStyleClass(name='PetImageCaption', fontName=std_italic_font, fontSize=11, alignment=TA_CENTER, textColor=COLOR_BODY_TEXT_DARK, spaceBefore=0.1*inch, spaceAfter=0.2*inch))
        self.logger.info(f"{self.__class__.__name__}: Base styles created. Sans: '{std_font}', Bold Sans: '{std_bold_font}'.")
        return styles

    def _add_image(self, image_source, story_list, width=None, height=None, preserveAspectRatio=False, hAlign=None, alpha=1.0):
        if not (reportlab_available and Image and ImageReader): self.logger.warning("ReportLab Image/ImageReader not available."); return None
        try:
            if image_source is None: self.logger.error("_add_image: image_source is None."); return None
            img = Image(str(image_source), width=width, height=height)
            img.preserveAspectRatio = preserveAspectRatio
            if hAlign: img.hAlign = hAlign
            story_list.append(img); return img
        except Exception as e:
            self.logger.error(f"_add_image: Error processing image {image_source}: {e}", exc_info=True)
            if story_list is not None and hasattr(self, 'styles') and self.styles and Paragraph and reportlab_available and hasattr(colors, 'red'):
                 story_list.append(Paragraph(f"[Err: Image {os.path.basename(str(image_source))}]", self.styles.get('Normal', ParagraphStyle('dummyError', textColor=colors.red, fontName=self.sans_font))))
            return None

    def build_pdf_story(self):
        if not (reportlab_available and BaseDocTemplate and PageTemplate and Frame):
            self.logger.critical(f"{self.__class__.__name__}.build_pdf_story: ReportLab components missing."); return False
        page_width, page_height = letter
        self.doc = BaseDocTemplate(self.output_path, pagesize=(page_width, page_height), leftMargin=1*inch, rightMargin=1*inch, topMargin=1*inch, bottomMargin=1*inch, author="Paws & Planets", title=f"Report for {self.client_name}")
        # MODIFIED LINE: Removed page_number_offset from here, it's not directly used by NumberedCanvas in this custom footer logic
        self.doc.canvasmakerKW = {'client_name_for_footer': self.client_name}
        self.doc.canvasmaker = NumberedCanvas

        cover_frame = Frame(0,0,page_width,page_height, id='cover_f'); cover_tpl = PageTemplate(id='CoverPage', frames=[cover_frame], onPage=self._on_cover_page_draw)
        portrait_frame_padding = 0.75*inch
        portrait_frame = Frame(portrait_frame_padding, portrait_frame_padding, page_width-(2*portrait_frame_padding), page_height-(2*portrait_frame_padding), id='portrait_f')
        portrait_tpl = PageTemplate(id='PortraitPage', frames=[portrait_frame], onPage=self._on_portrait_page_draw)
        main_frame = Frame(1*inch, 1*inch, self.doc.width, self.doc.height, id='main_f')
        main_tpl = PageTemplate(id='MainPage', frames=[main_frame], onPage=self._on_main_page_draw)

        # <<< NEW CODE START >>>
        # Template for full page section images
        full_image_frame = Frame(0, 0, page_width, page_height, id='full_image_f', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        full_image_tpl = PageTemplate(id='FullImagePage', frames=[full_image_frame], onPage=self._on_full_image_page_draw)
        self.doc.addPageTemplates([cover_tpl, portrait_tpl, main_tpl, full_image_tpl])
        # <<< NEW CODE END >>>

        self.story = []
        self.logger.info(f"{self.__class__.__name__}.build_pdf_story for {self.client_name} (templates set up).")
        return True

    def _on_cover_page_draw(self, canvas, doc):
        self.logger.debug(f"===> Executing _on_cover_page_draw for PDF page: {doc.page} <===")
        canvas.saveState()
        background_image_path_to_use = getattr(self, 'pet_background_cover_path', None)
        if background_image_path_to_use and os.path.exists(str(background_image_path_to_use)) and ImageReader:
            try:
                canvas.drawImage(str(background_image_path_to_use), 0, 0, width=doc.pagesize[0], height=doc.pagesize[1], preserveAspectRatio=False, mask='auto')
                self.logger.debug(f"_on_cover_page_draw (Page {doc.page}): Drew species cover image {background_image_path_to_use}.")
            except Exception as e_bg_draw:
                self.logger.error(f"Error drawing species cover image {background_image_path_to_use}: {e_bg_draw}. Falling back to color.")
                canvas.setFillColor(COLOR_PAGE_BACKGROUND); canvas.rect(0,0,doc.pagesize[0],doc.pagesize[1],stroke=0,fill=1)
        else:
            if background_image_path_to_use: self.logger.warning(f"Species cover image not found: {background_image_path_to_use}. Using color.")
            else: self.logger.debug(f"No species cover image path defined. Using color for Page 1.")
            canvas.setFillColor(COLOR_PAGE_BACKGROUND); canvas.rect(0,0,doc.pagesize[0],doc.pagesize[1],stroke=0,fill=1)
        canvas.restoreState()
        self.logger.debug(f"===> Finished _on_cover_page_draw for PDF page: {doc.page} <===")

    def _on_portrait_page_draw(self, canvas, doc):
        self.logger.debug(f"===> Executing _on_portrait_page_draw for PDF page: {doc.page} <===")
        canvas.saveState()
        if reportlab_available and hasattr(colors, 'white'):
            self.logger.debug(f"===> _on_portrait_page_draw - Filling with OPAQUE WHITE for PDF page: {doc.page} <===")
            canvas.setFillColor(colors.white) # Ensure opaque background if portrait has transparency
            canvas.rect(0,0,doc.pagesize[0],doc.pagesize[1],stroke=0,fill=1)
        # Then draw intended background for portrait page if different, or keep it white
        # For now, let's assume portrait page also uses COLOR_PAGE_BACKGROUND or the image fills it.
        # If the portrait image itself is a full page background, this might be redundant.
        # If portrait page needs a different background than COLOR_PAGE_BACKGROUND, set it here.
        # For consistency with main pages, if portrait frame doesn't fill, using COLOR_PAGE_BACKGROUND is good.
        canvas.setFillColor(COLOR_PAGE_BACKGROUND)
        canvas.rect(0,0,doc.pagesize[0],doc.pagesize[1],stroke=0,fill=1)
        canvas.restoreState()
        self.logger.debug(f"===> Finished _on_portrait_page_draw for PDF page: {doc.page} <===")

    # <<< NEW CODE START >>>
    def _on_full_image_page_draw(self, canvas, doc):
        self.logger.debug(f"===> Executing _on_full_image_page_draw for PDF page: {doc.page} <===")
        canvas.saveState()
        # This method is for the template used by full-page section images.
        # The image itself will be a flowable.
        # This onPage can set a default background if images have transparency or one is missing,
        # but since the images are 8.5x11, they should cover the page.
        # A simple white background ensures no weird artifacts if an image is slightly off.
        if reportlab_available and hasattr(colors, 'white'):
            canvas.setFillColor(colors.white) 
            canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], stroke=0, fill=1)
        self.logger.debug(f"Prepared canvas for full page image on PDF page: {doc.page}")
        canvas.restoreState()
        self.logger.debug(f"===> Finished _on_full_image_page_draw for PDF page: {doc.page} <===")
    # <<< NEW CODE END >>>

    def _on_main_page_draw(self, canvas, doc):
        self.logger.debug(f"===> Executing _on_main_page_draw for PDF page: {doc.page} <===")
        canvas.saveState()
        canvas.setFillColor(COLOR_PAGE_BACKGROUND)
        canvas.rect(0,0,doc.pagesize[0],doc.pagesize[1],stroke=0,fill=1)

        # <<< NEW CODE START >>> : Adjusted Page Numbering Logic
        # Define the number of pages at the beginning that are not part of the main numbered content flow
        # Cover, Portrait, Chart Wheel, Snapshot Table, TOC = 5 pages
        NUM_FRONT_MATTER_PAGES_BEFORE_MAIN_CONTENT_NUMBERING = 5
        
        # Main content pages are those using MainPage template AND are actual textual sections
        # Each textual section is preceded by a full image page.
        # The first *textual content section* will appear after the front matter and its own image page.
        # e.g., PDF Page 1-5 (Front Matter), P6 (Image for Sect 1), P7 (Sect 1 Text)
        first_numbered_content_section_pdf_page = NUM_FRONT_MATTER_PAGES_BEFORE_MAIN_CONTENT_NUMBERING + 2 # +1 for its image, +1 for itself

        if doc.page >= first_numbered_content_section_pdf_page:
            # Check if the current PDF page (doc.page) is a content text page
            # A content text page will occur after an even number of pages (image_page + text_page pairs)
            # after the initial front matter.
            # (doc.page - NUM_FRONT_MATTER_PAGES_BEFORE_MAIN_CONTENT_NUMBERING) will be an EVEN number for a content page.
            # Example: Page 7 (Sect 1 Text): (7 - 5) = 2 (even). Logical page = 2 / 2 = 1.
            # Page 9 (Sect 2 Text): (9 - 5) = 4 (even). Logical page = 4 / 2 = 2.
            page_diff_from_front_matter = doc.page - NUM_FRONT_MATTER_PAGES_BEFORE_MAIN_CONTENT_NUMBERING
            if page_diff_from_front_matter > 0 and page_diff_from_front_matter % 2 == 0:
                logical_footer_page_num = page_diff_from_front_matter // 2
                canvas.setFont(self.sans_font, 8); canvas.setFillColor(COLOR_FOOTER_TEXT)
                canvas.drawString(1*inch, 0.5*inch, getattr(canvas, 'client_name_for_footer', self.client_name))
                canvas.drawRightString(doc.pagesize[0] - 1*inch, 0.5*inch, f"Page {logical_footer_page_num}")
        # <<< NEW CODE END >>>
        canvas.restoreState()
        self.logger.debug(f"===> Finished _on_main_page_draw for PDF page: {doc.page} <===")

pdf_generator_version_marker = "1.1.35" # MODIFIED LINE

class PetPDFBuilder(BasePDFBuilder):
    def __init__(self, output_path, generation_context):
        super().__init__(output_path, generation_context)
        self.is_pet_report = True
        self.species = generation_context.get('species', 'other')
        if isinstance(self.species, str): self.species = self.species.lower()
        else: self.species = 'other'; self.logger.warning(f"Species not string: {generation_context.get('species')}")
        self.pet_info = { "pet_name": self.generation_context.get('client_name', "Your Pet") }
        self.occasion_mode = self.generation_context.get("occasion_mode", "pet_default")
        self.pet_sound = generation_context.get('pet_sound', 'unique sound')

        self.decorative_cover_image_path_species = os.path.join(self.images_dir, "covers", f"cover_pet_{self.species}.png")
        self.default_decorative_cover_other_path = os.path.join(self.images_dir, "covers", "default_pet_cover_other.png")
        potential_decorative_cover = self.decorative_cover_image_path_species
        if not os.path.exists(potential_decorative_cover):
            self.logger.warning(f"Species-specific cover ({potential_decorative_cover}) not found. Trying default.")
            potential_decorative_cover = self.default_decorative_cover_other_path
            if not os.path.exists(potential_decorative_cover):
                self.logger.error(f"Default pet cover ({potential_decorative_cover}) also not found. Cover will be plain parchment.")
                potential_decorative_cover = None
        self.pet_background_cover_path = potential_decorative_cover
        self.logger.info(f"PetPDFBuilder cover path for Page 1: {self.pet_background_cover_path}")

    def _create_styles(self):
        styles = super()._create_styles()
        std_font = self.sans_font; std_bold_font = self.sans_bold_font
        if styles.get('H1Style'): styles['H1Style'].leading = 24*1.3

        styles.add(_ParaStyleClass(name='PetTitleBlock', fontName=std_bold_font, fontSize=24, alignment=TA_CENTER, textColor=COLOR_HEADER_TEAL, spaceAfter=0.05*inch, leading=24*1.2, spaceBefore=0.2*inch))
        styles.add(_ParaStyleClass(name='PetMainTitle', fontName=std_bold_font, fontSize=36, alignment=TA_CENTER, textColor=COLOR_HEADER_TEAL, spaceAfter=0.1*inch, leading=36*1.2))
        styles.add(_ParaStyleClass(name='PetSubtitle', fontName=std_font, fontSize=16, alignment=TA_CENTER, textColor=COLOR_BODY_TEXT_DARK, spaceAfter=0.3*inch, leading=16*1.3))
        if styles.get('PetImageCaption'): styles['PetImageCaption'].fontName = self.sans_italic_font; styles['PetImageCaption'].spaceAfter = 0.1*inch

        styles.add(_ParaStyleClass(name='PetDividerTitle', fontName=std_bold_font, fontSize=22, alignment=TA_CENTER, textColor=COLOR_HEADER_TEAL, spaceBefore=1.5*inch, leading=22*1.2))
        styles.add(_ParaStyleClass(name='PetBlueprintSubtitle', fontName=std_font, fontSize=28, alignment=TA_CENTER, textColor=COLOR_BODY_TEXT_DARK, spaceAfter=0.3*inch, leading=28*1.2))

        styles.add(_ParaStyleClass(name='TableTitleStyle', fontName=std_bold_font, fontSize=22, alignment=TA_CENTER, textColor=COLOR_HEADER_TEAL, spaceBefore=0.5*inch, spaceAfter=0.4*inch))

        styles.add(_ParaStyleClass(name='PetMain', parent=styles['SectionTitle'], fontName=std_font, fontSize=24, alignment=TA_CENTER, textColor=COLOR_HEADER_TEAL, spaceBefore=0.5*inch, spaceAfter=0.2*inch))
        self.logger.info(f"PetPDFBuilder: Styles refined. Sans: '{std_font}', Bold Sans: '{std_bold_font}'.")
        return styles

    def _get_section_divider_path(self, section_id_tag="default"):
        tag_to_match = str(section_id_tag).lower().strip() if section_id_tag else "default"
        global STRIP_DIVIDERS
        divider_filename = STRIP_DIVIDERS.get(tag_to_match)
        if not divider_filename and tag_to_match != "toc": divider_filename = STRIP_DIVIDERS.get("default")
        if divider_filename:
            path_to_try = os.path.join(self.images_dir, "dividers", divider_filename)
            if os.path.exists(path_to_try): return path_to_try
            else: self.logger.warning(f"Divider image file '{divider_filename}' (tag '{tag_to_match}') NOT FOUND at {path_to_try}.")
        elif tag_to_match != "toc": self.logger.warning(f"No divider filename for tag '{tag_to_match}'.")
        return None

    def _build_pet_portrait_title_page_flowables(self):
        flowables = []
        pet_name = self.pet_info.get("pet_name", "Your Pet")
        species_cap = str(self.generation_context.get('species', 'Companion')).capitalize()
        custom_pet_image_url = self.generation_context.get("custom_pet_image_url")

        frame_content_width = self.doc.pagesize[0] - (2 * inch) - (2 * 0.75 * inch) if hasattr(self.doc, 'pagesize') else 5.0 * inch
        image_render_width = frame_content_width * 0.75

        flowables.append(Spacer(1, 0.5 * inch))
        flowables.append(Paragraph(f"Paws & Planets:", self.styles["PetTitleBlock"]))
        flowables.append(Paragraph(f"{pet_name}’s Starry Sniffari", self.styles["PetMainTitle"]))
        flowables.append(Paragraph(f"An Astrological Pawtrait for Your Beloved {species_cap}", self.styles["PetSubtitle"]))

        if custom_pet_image_url:
            flowables.append(Spacer(1, 0.4 * inch))
            image_path_resolved = None; temp_image_file_path = None
            if custom_pet_image_url.startswith("http"):
                try:
                    response = requests.get(custom_pet_image_url, stream=True); response.raise_for_status()
                    temp_dir = "/tmp"
                    if not os.path.exists(temp_dir): os.makedirs(temp_dir, exist_ok=True)
                    temp_image_file_path = os.path.join(temp_dir, f"{uuid.uuid4()}_pet_portrait_dl.img")
                    with open(temp_image_file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192): f.write(chunk)
                    image_path_resolved = temp_image_file_path
                except Exception as e: self.logger.error(f"Page 2 Image Download Fail: {e}")
            elif custom_pet_image_url.startswith("file://"): image_path_resolved = custom_pet_image_url.replace("file://", "", 1)
            else: image_path_resolved = custom_pet_image_url

            if image_path_resolved and os.path.exists(image_path_resolved):
                self._add_image(image_path_resolved, flowables, width=image_render_width, preserveAspectRatio=True, hAlign="CENTER")
                flowables.append(Spacer(1, 0.1 * inch))
                flowables.append(Paragraph(f"A Cosmic Portrait of {pet_name}", self.styles["PetImageCaption"]))
            else:
                self.logger.warning(f"Page 2 custom pet image not found/accessible: {custom_pet_image_url}. Using placeholder text.")
                flowables.append(Spacer(1, 0.2 * inch))
                flowables.append(Paragraph(f"Celebrating {pet_name}", self.styles["PetImageCaption"]))
            if temp_image_file_path and os.path.exists(temp_image_file_path):
                try: os.remove(temp_image_file_path)
                except OSError: pass
        else:
            flowables.append(Spacer(1, 0.4 * inch))
            flowables.append(Paragraph(f"Celebrating {pet_name}", self.styles["PetImageCaption"]))
        return flowables

    def _build_chart_snapshot_table(self):
        if not (reportlab_available and Table and TableStyle and Paragraph and hasattr(colors, 'darkgrey')):
            self.logger.warning("ReportLab Table components or specific colors not available for snapshot."); return []
        chart_data = self.generation_context.get("chart_data", {})
        positions = chart_data.get('positions', {}); chart_signatures = chart_data.get('chart_signatures', {}); birth_details = chart_data.get('birth_details', {})

        sun_sign_val = positions.get('Sun', {}).get('sign', 'N/A')
        moon_sign_val = positions.get('Moon', {}).get('sign', 'N/A')
        dom_element_val = chart_signatures.get('dominant_element_1', 'N/A')
        chart_ruler_val = birth_details.get('chart_ruler', 'N/A')
        modality_val = chart_signatures.get('dominant_modality_1', 'N/A')
        birth_loc_val = f"{birth_details.get('city', 'N/A')}, {birth_details.get('country_code', 'N/A')}"

        planet_symbols = {"Sun":"☉","Moon":"☽","Mercury":"☿","Venus":"♀","Mars":"♂","Jupiter":"♃","Saturn":"♄","Uranus":"♅","Neptune":"♆","Pluto":"♇"}
        element_symbols = {"Fire":"🔥","Earth":"🌍","Air":"💨","Water":"💧"}

        sun_sign_display = f"{sun_sign_val} {planet_symbols.get('Sun','')}".strip() if sun_sign_val != 'N/A' else 'N/A'
        moon_sign_display = f"{moon_sign_val} {planet_symbols.get('Moon','')}".strip() if moon_sign_val != 'N/A' else 'N/A'
        dom_element_display = f"{dom_element_val} {element_symbols.get(dom_element_val,'')}".strip() if dom_element_val != 'N/A' else 'N/A'

        chart_ruler_display = chart_ruler_val
        if chart_ruler_val != 'N/A':
            for p,s_char in planet_symbols.items():
                if p in chart_ruler_val: chart_ruler_display = chart_ruler_val.replace(p,f"{p} {s_char}"); break

        data_for_table = [["Trait","Value"],["Sun Sign",sun_sign_display],["Moon Sign",moon_sign_display],["Dominant Element",dom_element_display],["Chart Ruler",chart_ruler_display],["Modality",modality_val],["Birth Location",birth_loc_val]]
        cell_style = ParagraphStyle(name='TableCellSnap', fontName=self.sans_font, fontSize=11, textColor=COLOR_BODY_TEXT_DARK, leading=14)
        header_cell_style = ParagraphStyle(name='TableHeaderCellSnap', fontName=self.sans_bold_font, fontSize=12, textColor=COLOR_HEADER_TEAL, leading=15)
        styled_data = [[Paragraph(str(ct if ct is not None else 'N/A'), header_cell_style if ir==0 else cell_style) for ct in rc] for ir,rc in enumerate(data_for_table)]
        table_obj = Table(styled_data, colWidths=[2.0*inch,3.5*inch])
        table_obj.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.darkgrey),('BACKGROUND',(0,0),(-1,0),lightgrey),('ALIGN',(0,0),(-1,-1),'LEFT'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('FONTNAME',(0,0),(-1,0),self.sans_bold_font),('FONTNAME',(0,1),(-1,-1),self.sans_font)]))
        return [table_obj]

    def build_pdf_story(self): # MODIFIED LINE to reflect it's from PetPDFBuilder
        if not super().build_pdf_story(): return False # Calls BasePDFBuilder's build_pdf_story to set up doc and common templates
        pet_name = self.pet_info.get("pet_name", "Your Pet")

        # --- Page 1: Cover ---
        self.story.append(NextPageTemplate('CoverPage'))
        self.story.append(Spacer(1, 0.01*inch)) 
        self.story.append(PageBreak())
        self.logger.debug("===> BUILD STORY: Added CoverPage elements for Page 1 <===")

        # --- Page 2: Portrait & Title ---
        self.story.append(NextPageTemplate("PortraitPage"))
        self.story.append(Spacer(1, 0.01*inch)) 
        self.story.extend(self._build_pet_portrait_title_page_flowables())
        self.story.append(PageBreak())
        self.logger.debug("===> BUILD STORY: Added PortraitPage elements for Page 2 <===")

        # --- Page 3: Chart Wheel ---
        self.story.append(NextPageTemplate("MainPage")) # Chart wheel uses MainPage template
        self.story.append(Spacer(1, 0.01*inch)) 
        chart_img_path = self.generation_context.get('chart_image_path')
        if chart_img_path and os.path.exists(str(chart_img_path)):
            self.story.append(Paragraph(_clean_mika_voice("Your Pet's Cosmic Blueprint (Chart Wheel)"), self.styles.get('H1Style')))
            self.story.append(Spacer(1,0.15*inch))
            self._add_image(chart_img_path,self.story,width=400,height=400,preserveAspectRatio=True,hAlign='CENTER')
            self.story.append(PageBreak())
            self.logger.debug("===> BUILD STORY: Added Chart Image elements for Page 3 <===")
        else:
            self.logger.info("Chart image path not provided or image not found. Page 3 (Chart Wheel) will be effectively skipped.")
            self.logger.debug("===> BUILD STORY: No Chart Image for Page 3. <===")

        # --- Page 4 (or 3 if no chart): Astrological Summary Table ---
        # This also uses MainPage template
        self.story.append(Paragraph(f"Cosmic Snapshot of {pet_name}", self.styles.get('TableTitleStyle')))
        self.story.extend(self._build_chart_snapshot_table())
        self.story.append(PageBreak())
        self.logger.debug("===> BUILD STORY: Added Snapshot Table elements <===")

        # --- Page 5 (or 4): Table of Contents ---
        # This also uses MainPage template
        self.story.append(Paragraph("Table of Contents", self.styles.get('TOCReportHeader')))
        toc_items = []; sections_data = self.generation_context.get('sections', [])
        actual_content_sections = [s for s in sections_data if isinstance(s,dict) and s.get('divider_tag')!='toc' and not (s.get('section_id')=='fixed_stars' and self.generation_context.get('skip_fixed_stars'))]

        # Manually add fixed front matter titles to TOC items list before looping actual_content_sections
        toc_fixed_front_matter_titles = []
        if chart_img_path and os.path.exists(str(chart_img_path)):
            toc_fixed_front_matter_titles.append("Your Pet's Cosmic Blueprint (Chart Wheel)")
        toc_fixed_front_matter_titles.append(f"Cosmic Snapshot of {pet_name}") # Title for snapshot table page

        current_toc_item_number = 0
        for title in toc_fixed_front_matter_titles:
            current_toc_item_number += 1
            self.story.append(Paragraph(f"{current_toc_item_number}. {str(title)}", self.styles.get('TOCEntryStyle')))
        
        for sec in actual_content_sections: # These are the main text sections that will follow images
            title_raw = sec.get('meta',{}).get('section_title') or sec.get('header','Unnamed Section')
            title_clean = _clean_mika_voice(str(title_raw))
            try: title_fmt = title_clean.format(pet_name=pet_name, species=self.species.capitalize(), pet_sound=self.pet_sound)
            except Exception: title_fmt = title_clean
            
            current_toc_item_number += 1 # For the image page
            # TOC entry for the image page (optional, could be skipped or styled differently)
            # self.story.append(Paragraph(f"{current_toc_item_number}. Image: {str(title_fmt or 'Unnamed Section')}", self.styles.get('TOCEntryStyle'))) 
            
            current_toc_item_number += 1 # For the content page
            self.story.append(Paragraph(f"{current_toc_item_number}. {str(title_fmt or 'Unnamed Section')}", self.styles.get('TOCEntryStyle')))

        if not toc_fixed_front_matter_titles and not actual_content_sections:
             self.story.append(Paragraph("No sections in TOC.", self.styles.get('Normal')))
        
        self.story.append(PageBreak())
        self.logger.debug("===> BUILD STORY: Added TOC elements <===")

        # --- Page 6+ (or 5+): Section Content with Full Page Images Before Each ---
        num_content_sections = len(actual_content_sections)
        for idx, section in enumerate(actual_content_sections):
            # <<< NEW CODE START >>>
            section_image_number = idx + 1 # section1.png for actual_content_sections[0], etc.
            section_image_filename = f"section{section_image_number}.png"
            section_image_path = os.path.join(self.images_dir, section_image_filename)

            if os.path.exists(section_image_path):
                self.story.append(NextPageTemplate("FullImagePage")) 
                self.story.append(PageBreak())
                
                # Image should be 8.5 x 11 inches (letter size in points: 612 x 792)
                img_flowable = Image(section_image_path, width=self.doc.pagesize[0], height=self.doc.pagesize[1], preserveAspectRatio=False)
                self.story.append(img_flowable)
                
                self.logger.debug(f"===> BUILD STORY: Added full page image {section_image_filename} before section '{section.get('header', 'Unknown')}' <===")
            else:
                self.logger.warning(f"===> BUILD STORY: Full page section image NOT FOUND: {section_image_path}. Skipping image for section '{section.get('header', 'Unknown')}' <===")
                # Optionally, add a blank page or a placeholder if an image is missing but you want to maintain page flow
                # self.story.append(NextPageTemplate("FullImagePage")) # Use if you want a blank page from this template
                # self.story.append(PageBreak())
                # self.story.append(Spacer(1,0.01*inch)) # Minimal flowable for the blank page

            self.story.append(NextPageTemplate("MainPage")) 
            self.story.append(PageBreak())
            # <<< NEW CODE END >>>

            header = _clean_mika_voice(str(section.get('header','Unnamed Section')))
            self.story.append(Paragraph(header, self.styles.get('H1Style')))
            quote = section.get('quote')
            if quote: self.story.append(Paragraph(_clean_mika_voice(str(quote)), self.styles.get('PetQuoteStyle')))

            ai_content = _clean_mika_voice(str(section.get('ai_content','')))
            self.story.append(Paragraph(str(ai_content).replace("\n","<br/>"), self.styles.get('BodyText')))

            # Divider image after content, before page break to next section (or end)
            divider_path = self._get_section_divider_path(section.get('divider_tag', section.get('section_id')))
            if divider_path:
                self.story.append(Spacer(1,0.2*inch)); self._add_image(divider_path,self.story,width=(self.doc.width*0.8 if hasattr(self.doc,'width') else 5*inch),height=0.8*inch,preserveAspectRatio=True,hAlign='CENTER'); self.story.append(Spacer(1,0.1*inch))
            else: self.story.append(Spacer(1,0.25*inch))
            
            # Only add a PageBreak if it's not the very last content section
            if idx < num_content_sections - 1:
                 self.story.append(PageBreak())
        self.logger.debug("===> BUILD STORY: Finished adding main content sections <===")

        try:
            self.logger.info(f">>> BUILDING PDF (V{pdf_generator_version_marker}) WITH {len(self.story)} flowables for: {self.output_path}")
            self.doc.multiBuild(self.story)
            self.logger.info(f"PDF built successfully: {self.output_path}"); return True
        except Exception as e: self.logger.critical(f"PDF generation FAILED during multiBuild: {e}", exc_info=True); return False

# --- Main PDF Generation Function ---
def generate_astrology_pdf( output_path, generation_context=None, **kwargs):
    logger.info(f"PetPDFBuilder Module: Initiating PET PDF generation (V{pdf_generator_version_marker}) for client: {generation_context.get('client_name', 'Unknown') if generation_context else kwargs.get('client_name', 'Unknown')}")
    if generation_context is None:
        logger.warning("generation_context not provided directly, constructing from kwargs.")
        generation_context = kwargs.copy()
        generation_context.setdefault('client_name', 'Valued Pet'); generation_context.setdefault('species', 'companion')
        generation_context.setdefault('occasion_mode', 'pet_default'); generation_context.setdefault('pronoun_mode', 'name')
        generation_context.setdefault('skip_fixed_stars', False); generation_context.setdefault('sections', [])
        generation_context.setdefault('chart_data', {}); generation_context.setdefault('PET_PROMPTS', {})
        generation_context.setdefault('SECTION_LAYOUT_PRESETS', {})
    else:
        logger.debug("generation_context was provided directly.")
        for key, val_from_kwarg in kwargs.items():
            if key not in generation_context or generation_context.get(key) is None:
                if val_from_kwarg is not None:
                    generation_context[key] = val_from_kwarg
                    logger.debug(f"Updated generation_context with '{key}' from direct kwarg.")
    generation_context.setdefault('custom_pet_image_url', None)
    generation_context.setdefault('pronoun_mode', generation_context.get('pronoun_mode', 'name'))

    try:
        builder = PetPDFBuilder(output_path, generation_context)
        success = builder.build_pdf_story()
        final_client_name_log = generation_context.get('client_name', 'Unknown Client')
        if success: logger.info(f"Pet PDF generated successfully for {final_client_name_log}: {output_path}")
        else: logger.error(f"PDF generation FAILED for {final_client_name_log}: {output_path}")
        return success
    except Exception as e:
        final_client_name_exc_log = generation_context.get('client_name', 'Unknown Client')
        logger.critical(f"PetPDFBuilder Module: [FATAL] PDF generation exception for {final_client_name_exc_log}: {e}", exc_info=True)
        return False

# --- Global STRIP_DIVIDERS definition ---
STRIP_DIVIDERS = {
  "toc": None, "prologue": "2_once_upon.png", "chart_wheel": "3_cosmic_collar.png",
  "sun": "4_solar.png", "moon": "5_moonpaw.png", "rising": "6_tail.png",
  "element_modality": "7_elementspaw.png", "aspects": "8_playdatespaw.png",
  "balance": "strip_pet_heart.png", "karmic_lesson": "10_karmakibbles.png",
  "north_node": "11_furtune.png", "care_tips": "12_star.png", "breed_spotlight":  "13_breed.png",
  "footer": "14_cosmic_companion.png", "default": "strip_pet_heart.png",
  "fixed_stars": "strip_pet_celestial.png", "mercury_sign": "strip_pet_quill.png",
  "venus_sign": "strip_pet_rose.png", "mars_sign": "strip_pet_comet.png",
  "chiron": "strip_pet_healingpaw.png", "black_moon_lilith": "strip_pet_moonphase.png",
  "south_node": "strip_pet_pastlife.png", "dominant_combinations": "strip_pet_constellation.png",
  "element_balance": "strip_pet_elements.png", "karmic_lessons": "10_karmakibbles.png",
  "snack_and_snooze": "strip_pet_bowl.png", "breed_o_scope": "13_breed.png",
  "companion_care": "12_star.png"
}

# --- Main Execution Block for Testing ---
if __name__ == '__main__':
    test_logger_main = logging.getLogger(__name__)

    if not reportlab_available:
        test_logger_main.error("TEST CANCELED: ReportLab library is not available.")
    else:
        test_logger_main.info(f"--- Running PDF Generation Test (V{pdf_generator_version_marker} - ADD FULL PAGE SECTION IMAGES) ---")

        test_base_dir = SCRIPT_DIR_PET
        project_root_for_test = PROJECT_ROOT_PET
        common_fonts_dir_for_test = os.path.join(project_root_for_test, "common", "fonts")
        os.makedirs(common_fonts_dir_for_test, exist_ok=True)
        local_assets_dir_for_test = os.path.join(test_base_dir, 'assets')
        images_test_dir = os.path.join(local_assets_dir_for_test, 'images') # MODIFIED LINE
        os.makedirs(os.path.join(images_test_dir, 'covers'), exist_ok=True)
        os.makedirs(os.path.join(images_test_dir, 'dividers'), exist_ok=True)

        # Ensure a dummy cover image exists for testing the onPageDraw logic
        dummy_cover_image_path = os.path.join(images_test_dir, "covers", "cover_pet_cat.png") # MODIFIED LINE
        if not os.path.exists(dummy_cover_image_path):
            try:
                from PIL import Image as PILImage, ImageDraw
                img_cover = PILImage.new('RGB', (612, 792), color = 'green') # Letter size in points
                d_cover = ImageDraw.Draw(img_cover)
                d_cover.text((100,100), "Dummy Cat Cover", fill=(255,255,255))
                img_cover.save(dummy_cover_image_path)
                test_logger_main.info(f"Created dummy cover image: {dummy_cover_image_path}")
            except ImportError:
                test_logger_main.warning("Pillow not available. Cannot create dummy cover image for test. Cover page may be blank if original is missing.")


        dummy_chart_image_for_test_path = os.path.join(images_test_dir, "test_dummy_chart.png") # MODIFIED LINE
        if not os.path.exists(dummy_chart_image_for_test_path):
            try:
                from PIL import Image as PILImage, ImageDraw
                img = PILImage.new('RGB', (100, 100), color = 'red')
                d = ImageDraw.Draw(img)
                d.text((10,10), "Dummy Chart", fill=(255,255,0))
                img.save(dummy_chart_image_for_test_path)
                test_logger_main.info(f"Created dummy chart image for test: {dummy_chart_image_for_test_path}")
            except ImportError:
                test_logger_main.warning("Pillow not available. Cannot create dummy chart image for test.")
                dummy_chart_image_for_test_path = None
        
        # <<< NEW CODE START >>> Create dummy section images for testing
        for i in range(1, 3): # Create section1.png and section2.png for the test
            dummy_section_image_path = os.path.join(images_test_dir, f"section{i}.png")
            if not os.path.exists(dummy_section_image_path):
                try:
                    from PIL import Image as PILImage, ImageDraw
                    # Letter size in points: 8.5*72=612, 11*72=792
                    img_sec = PILImage.new('RGB', (612, 792), color = random.choice(['lightblue', 'lightcoral', 'lightgoldenrodyellow'])) 
                    d_sec = ImageDraw.Draw(img_sec)
                    d_sec.text((50,300), f"Dummy Image for Section {i}\n8.5 x 11 inches", fill=(0,0,0), font_size=40) # Requires font object in real use
                    img_sec.save(dummy_section_image_path)
                    test_logger_main.info(f"Created dummy section image for test: {dummy_section_image_path}")
                except ImportError:
                    test_logger_main.warning(f"Pillow not available. Cannot create dummy section {i} image for test.")
        # <<< NEW CODE END >>>


        for font_filename in ["DejaVuSans.ttf", "DejaVuSans-Bold.ttf"]:
            font_path_in_common = os.path.join(common_fonts_dir_for_test, font_filename)
            if not os.path.exists(font_path_in_common):
                with open(font_path_in_common, "wb") as f_dummy: f_dummy.write(b"dummy font for " + font_filename.encode())
                test_logger_main.info(f"Created dummy font for testing in common/fonts: {font_path_in_common}")

        test_output_dir = os.path.join(test_base_dir, "test_pdf_output_FULL_SECTION_IMAGES") # MODIFIED LINE
        os.makedirs(test_output_dir, exist_ok=True)
        final_test_path = os.path.join(test_output_dir, "FULL_SECTION_IMAGES_Luna_Memorial.pdf") # MODIFIED LINE

        dummy_pet_image_path = os.path.join(images_test_dir, "test_luna_portrait.png") # MODIFIED LINE
        if not os.path.exists(dummy_pet_image_path):
            try:
                from PIL import Image as PILImage, ImageDraw
                img_pet = PILImage.new('RGB', (200, 200), color = 'blue')
                d_pet = ImageDraw.Draw(img_pet)
                d_pet.text((10,10), "Luna Portrait", fill=(255,255,255))
                img_pet.save(dummy_pet_image_path)
                test_logger_main.info(f"Created dummy pet portrait for test: {dummy_pet_image_path}")
            except ImportError:
                test_logger_main.warning("Pillow not available. Cannot create dummy pet portrait for test.")
                dummy_pet_image_path = None


        test_sections = [
            {"section_id": "sun_sign", "header": "{pet_name}'s Radiant Sun", "meta": {"section_title": "{pet_name}'s Sun Sign"}, "ai_content": "Sun content for Luna. This section should be preceded by section1.png.", "quote":"'I am magnificent!' - Luna"},
            {"section_id": "moon_sign", "header": "{pet_name}'s Gentle Moon", "meta": {"section_title": "{pet_name}'s Moon Moods"}, "ai_content": "Moon details for Luna. This section should be preceded by section2.png.", "quote":"Home is where the heart is."},
        ]
        test_chart_data = {
            "birth_details": {"name": "Luna", "city": "Starville", "country_code": "SV", "chart_ruler": "Sun ☉"},
            "positions": {"Sun": {"sign": "Leo"}, "Moon": {"sign": "Cancer"}}, "angles": {"Ascendant":{"sign":"Virgo"}},
            "chart_signatures": {"dominant_element_1": "Fire", "dominant_modality_1": "Fixed"}
        }

        context = {
            'client_name': "Luna", 'species': "Cat", 'occasion_mode': "pet_memorial", 'pronoun_mode': "she",
            'custom_pet_image_url': f"file://{os.path.abspath(dummy_pet_image_path)}" if dummy_pet_image_path and os.path.exists(dummy_pet_image_path) else None,
            'chart_image_path': os.path.abspath(dummy_chart_image_for_test_path) if dummy_chart_image_for_test_path and os.path.exists(dummy_chart_image_for_test_path) else None,
            'chart_data': test_chart_data, 'sections': test_sections,
            'assets_dir': local_assets_dir_for_test, # MODIFIED LINE
            'fonts_dir': FONTS_DIR_PET, # This should point to where your main fonts are, common/fonts might be better if DejaVu is there
            'data_jsons_dir': DATA_JSONS_DIR_PET, 'PET_PROMPTS': {}, 'SECTION_LAYOUT_PRESETS': {}
        }
        try:
            test_logger_main.info(f"Attempting PDF generation for: {final_test_path}")
            generate_astrology_pdf(output_path=final_test_path, generation_context=context)
            test_logger_main.info(f"Full Section Image Test PDF generation attempt finished: {final_test_path}")
        except Exception as e_main_test:
            test_logger_main.error(f"[FATAL] PDF generation test failed: {e_main_test}", exc_info=True)