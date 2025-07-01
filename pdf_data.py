from collections import defaultdict
from dataclasses import dataclass, field
from pdfplumber import open
from re import search, split, findall
from typing import List, Tuple
import tkinter as tk
import tkinter.ttk as ttk
import unicodedata

@dataclass
class address_info:
    name: str              = ''
    address: str           = ''
    city: str              = ''
    phone: str             = ''
    delivery_name: str     = ''
    delivery_address: str  = ''
    delivery_postcode: str = ''

@dataclass
class order_info:
    date: str = ''
    week: str = ''
    comm: str = ''

@dataclass
class article_info:
    backgrounds: List[Tuple[int, int]] = field(default_factory=list)
    colour: str                        = ''
    lakstift: str                      = ''
    afdekkap: str                      = ''
    num_glue: str                      = ''
    num_cleaner: str                   = ''
    num_kit_trans: str                 = ''
    num_kit_colour: str                = ''
    kit_colour: str                    = ''

def popup(text):
    window = tk.Toplevel()

    text = tk.Label(window, text=text)
    text.grid(row=0, column=0)

    button = ttk.Button(window, text='Sluit', command=window.destroy)
    button.grid(row=1, column=0)

class pdf_data:
    def __init__(self, filename):
        self.address_info = address_info()
        self.order_info = order_info()
        self.extra_info = []
        self.article_info = article_info()
        self.wrong = False

        with open(filename) as pdf:
            lines = defaultdict(str)
            for c in pdf.pages[0].chars:
                lines[c['top']] += c['text']
            
            lines = [ lines[key] for key in sorted(lines.keys()) ]

            self.address_info.name    = lines[1]
            self.address_info.address = lines[2]
            self.address_info.city    = lines[3]
            self.address_info.phone   = lines[5]
            self.address_info.delivery_name     = unicodedata.normalize("NFKD", lines[7])
            self.address_info.delivery_address  = unicodedata.normalize("NFKD", lines[8])
            self.address_info.delivery_postcode = unicodedata.normalize("NFKD", lines[9])

            # Split the contents of the PDF into address, order and article information.
            parts = split(r'ArtikelOmschrijvingAantalStuksprijsTotaal|Extra informatie:|Orderbevestiging', ''.join([c['text'] for c in pdf.pages[0].chars]))
            ord_info, art_info, extra_info, *_ = parts

            # Store the order information.
            try:
                _regex = search(r'Datum:(\d{2}-\d{2}-\d{4})Ordernummer:([\d\.]+)Commissie:(.*)Leverweek:(\d{4}-\d{2})', ord_info)
                self.order_info.date   = _regex.group(1)
                self.order_info.comm   = _regex.group(3)
                self.order_info.week   = _regex.group(4)
            except Exception:
                popup('Error: fout in ordergegevens.')
                self.wrong = True
                return

            if 'extra_info' in locals():
                split_word = 'Betalingsvoorwaarden' if 'Betalingsvoorwaarden' in extra_info else 'Indien u uiterlijk'

                self.extra_info = extra_info.split(split_word)[0].split(',')

                print(self.extra_info)

            # Store the article information.
            try:
                self.article_info.backgrounds = [ (int(x), int(y)) for (x,y) in findall(r'[AS]W\d{3}-\d{3}Bokmerk (?:Sanitair|Keuken)wandpaneel ?(\d+) x (\d+)', art_info)]
                self.article_info.colour = search(r'kleur: ([A-Za-z\s]+\d*) ', art_info).group(1)
                _regex = search(r'LIJMBokmerk Montagelijm koker(\d+)', art_info)
                self.article_info.num_glue = _regex.group(1) if _regex else ''
                _regex = search(r'K\d{2}Siliconenkit \| ([A-Z\d]+)(\d)', art_info)
                self.article_info.kit_colour = _regex.group(1) if _regex else ''
                self.article_info.num_kit_colour = _regex.group(2) if _regex else ''
                _regex = search(r'CLEANBokmerk Wandcleaner set(\d+)', art_info)
                self.article_info.num_cleaner = _regex.group(1) if _regex else ''
                _regex = search(r'LAKSTIFTLakstift \| kleur: [A-Za-z\s]+\d* (\d)', art_info)
                self.article_info.lakstift = _regex.group(1) if _regex else ''
                _regex = search(r'AKAfdekkap .*\| kleur: [A-Za-z\s]+\d*(\d)', art_info)
                self.article_info.afdekkap = _regex.group(1) if _regex else ''
            except Exception:
                popup('Error: fout in artikelen.')
                self.wrong = True
                return

