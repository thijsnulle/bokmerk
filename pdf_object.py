from fpdf import FPDF
from pdf_data import pdf_data
from PIL import Image
import datetime, os, re, string

def resource_path(relative_path):
    base_path = os.environ.get('RESOURCEPATH') if 'RESOURCEPATH' in os.environ else os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PDF(FPDF):

    def __init__(self, filename, draw_panels = True, image = None):
        super().__init__(orientation='L')
        self.pdf_data = pdf_data(filename)

        if self.pdf_data.wrong:
            return

        # Add page for XL panels.
        if any([ x > 4000 for (x, _) in self.pdf_data.article_info.backgrounds ]):
            self.add_page()
            self.add_information(True)
            if draw_panels:
                self.draw_panels([ (x,y) for (x,y) in self.pdf_data.article_info.backgrounds if x > 4000 ])
            if image:
                self.add_image(image)

        # Add page for non-XL panels.
        if any([ x <= 4000 for (x, _) in self.pdf_data.article_info.backgrounds ]):
            self.add_page()
            self.add_information(False)
            if draw_panels:
                self.draw_panels([ (x,y) for (x,y) in self.pdf_data.article_info.backgrounds if x <= 4000 ])
            if image:
                self.add_image(image)

        self.save(filename)

    def add_information(self, large_panels):
        self.set_xy(10.0, 10.0)
        self.set_font('Helvetica', 'B', size=16)
        self.cell(w=0, txt="BESTELFORMULIER")

        ### FIRST COLUMN ###
        self.set_font('Helvetica', size=9)
        for (y, desc, value) in zip([17,23,29,35,41], ['Besteldatum', 'Bedrijf', 'Plaats', 'Commissie', 'Telefoon'], [self.pdf_data.order_info.date, self.pdf_data.address_info.name, self.pdf_data.address_info.city, None, self.pdf_data.address_info.phone]):
            self.set_xy(10.0, y); self.cell(w=0, txt=desc)
            self.set_xy(31.0, y); self.cell(w=0, txt=value if value else '')
            self.line(31.0, y+2.0, 78.0, y+2.0)

        self.set_font('Helvetica', 'B', size=9)
        self.set_xy(31.0, 35.0); self.cell(w=0, txt=self.pdf_data.order_info.comm if self.pdf_data.order_info.comm else '')
        self.line(31.0, 37.0, 78.0, 37.0)

        ### SECOND COLUMN ###
        self.set_font('Helvetica', size=9)
        self.set_xy(80.0, 17.0); self.cell(w=0, txt='Kleur')
        self.set_xy(94.0, 17.0); self.cell(w=0, txt=self.pdf_data.article_info.colour)
        self.line(94.0, 19.0, 148.0, 19.0)

        backgrounds = [ (x,y) for (x,y) in self.pdf_data.article_info.backgrounds if (x > 4000) == large_panels]
        for (y, desc, value) in zip([23,29,35,41], ['Panelen', 'Lijm', 'Cleaner', 'Lakstift'], [str(len(backgrounds)), None, None, None]):
            self.set_xy(80.0, y); self.cell(w=0, txt=desc)
            self.set_xy(94.0, y); self.cell(w=6, align='C', txt=value if value else '')
            self.line(94.0, y+2.0, 100.0, y+2.0)

        for (y, desc) in zip([23,29,35,41], ['Kit trans', 'Kit kleur', 'Kleur kit', 'Afdekkap']):
            self.set_xy(102.0, y); self.cell(w=0, txt=desc)
            self.line(118.0, y+2.0, 148.0, y+2.0)

        if (any([ x <= 4000 for (x, _) in self.pdf_data.article_info.backgrounds ]) and not large_panels) or \
           (all([ x >  4000 for (x, _) in self.pdf_data.article_info.backgrounds ]) and     large_panels):
            for (y, value) in zip([23,29,35,41], [None, self.pdf_data.article_info.num_glue, self.pdf_data.article_info.num_cleaner, self.pdf_data.article_info.lakstift]):
                self.set_xy(94.0, y); self.cell(w=6, align='C', txt=value if value else '')

            for (y, value) in zip([23,29,35,41], [self.pdf_data.article_info.num_kit_trans, self.pdf_data.article_info.num_kit_colour, self.pdf_data.article_info.kit_colour, self.pdf_data.article_info.afdekkap]):
                self.set_xy(118.0, y); self.cell(w=30, align='C', txt=value if value else '')

        ### THIRD COLUMN ###
        self.set_font('Helvetica', size=9)
        for (y, desc, value) in zip([17,23,29,35,41], ['Orderweek', 'Afleveradres', '', '', ''], [self.pdf_data.order_info.week, None, self.pdf_data.address_info.delivery_address, self.pdf_data.address_info.delivery_postcode, None]):
            self.set_xy(150.0, y); self.cell(w=0, txt=desc)
            self.set_xy(171.0, y); self.cell(w=0, txt=value if value else '')
            self.line(171.0, y+2.0, 218.0, y+2.0)

        self.set_font('Helvetica', 'B', size=9)
        self.set_xy(171.0, 23.0); self.cell(w=0, txt=self.pdf_data.address_info.delivery_name if self.pdf_data.address_info.delivery_name else '')
        self.line(171.0, 25.0, 218.0, 25.0)

        ### FOURTH COLUMN ###
        self.set_font('Helvetica', size=9)
        for (y, desc) in zip([17,23,29,35,41], ['Opmerkingen', '', '', '', '']):
            self.set_xy(220.0, y); self.cell(w=0, txt=desc)
            self.line(242.0, y+2.0, 288.0, y+2.0)

        for (y, value) in zip([17,23,29,35,41], *[self.pdf_data.extra_info]):
            self.set_xy(242.0, y); self.cell(w=0, txt=value if value else '')

        self.image(resource_path('images/logo-bokmerk.png'), 240.0, 190.0, 50.0, 15.0)
        self.image(resource_path('images/legend.png'), 10.0, 195.0, 135.0, 15.0)


    def draw_panels(self, backgrounds):
        width = 278.0
        height = 138.0
        xx = min(len(backgrounds), 3)
        yy = (len(backgrounds) - 1) // 3 + 1
        w = width / xx; h = height / yy
        x = 10.0 + (width - xx * w) / 2; y = 50.0 + (height - h * yy) / 2

        for i, b in enumerate(backgrounds):
            self.draw_rect((x + (i % 3) * w, y + (i // 3) * h, h, w), b)

    def draw_rect(self, bbox, size):
        x, y, h, w = bbox
        width, height = (size[0], size[1])

        _w = w * (0.3 if max(width, height) <= 500 else 0.5 if max(width, height) <= 1000 else 0.85)
        if (height / h > width / w):
            _w = _w * ((width / w) / (height / h))

        _h = _w / (width/height)

        self.rect(x + w/2 - _w/2, y + h/2 - _h/2, _w, _h)
        self.set_xy(x + w/2 - _w/2, y + h/2 - _h/2 - 2.0); self.cell(w=_w, align='C', txt=str(width))
        self.set_xy(x + w/2 + _w/2, y + h/2); self.cell(w=0, txt=str(height))
        self.set_xy(x + w/2 - _w/2, y + h/2 + _h/2 + 2.0); self.cell(w=_w, align='C', txt=str('ophangoog'))


    def add_image(self, image):
        img = Image.open(image)
        if (img.size[0] < img.size[1]):
            output = img.rotate(90, expand = True)
            output.save(image)

        width, height = Image.open(image).size

        _w = 277.0
        _h = 143.0

        w = min(width, _w)
        h = w * (height/width)

        if h > _h:
            h = _h
            w = w * (h/_h)

        self.image(image, 15.0 + _w / 2 - w / 2, 45.0 + _h / 2 - h / 2, w, h)


    def save(self, filename):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = f'{directory}/' + re.sub(r'\s', '', f'{datetime.datetime.now().strftime("%d%m%Y")}_{self.pdf_data.address_info.name}_{self.pdf_data.order_info.comm}_{self.pdf_data.article_info.colour}.pdf')

        self.pages = { n:''.join(filter(lambda x: x in set(string.printable), page)) for n,page in self.pages.items() }
        self.output(filename)
