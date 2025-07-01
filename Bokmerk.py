from pdf_object import PDF
from PIL import Image, ImageTk
import os
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.ttk as ttk

root = tk.Tk();
root.title('Bokmerk v2.2')
root.geometry('400x250')

def popup(text, ok_text = 'Sluit', close_text = None):
    window = tk.Toplevel()

    text = tk.Label(window, text=text)
    text.grid(row=0, column=0)

    def method(value, window):
        global ok
        ok = value
        window.destroy()

    ok_button = ttk.Button(window, text=ok_text, command=lambda: method(True, window))
    ok_button.grid(row=1, column=0)

    if close_text:
        close_button = ttk.Button(window, text=close_text, command=lambda: method(False, window))
        close_button.grid(row=2, column=0)

    root.wait_window(window)
    return ok


def resource_path(relative_path):
    base_path = os.environ.get('RESOURCEPATH') if 'RESOURCEPATH' in os.environ else os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def generate():
    filenames = fd.askopenfilenames(parent=root)

    if len(filenames) == 0:
        popup('Selecteer minimaal 1 bestand.')
    elif len(filenames) == 1:
        if not filenames[0].lower().endswith('.pdf'):
            popup('Selecteer 1 PDF bestand.')

        PDF(filenames[0])
    elif len(filenames) == 2:
        if not any([ f.lower().endswith('.pdf') for f in filenames ]) or all([ f.lower().endswith('.pdf') for f in filenames ]):
            popup('Selecteer 1 PDF bestand en 1 afbeelding.')

        pdf_file = [ f for f in filenames if f.lower().endswith('.pdf') ][0]
        img_file = [ f for f in filenames if not f.lower().endswith('.pdf') ][0]

        PDF(pdf_file, False, img_file)
    elif all([ f.lower().endswith('.pdf') for f in filenames ]):
        for f in filenames:
            PDF(f)
    else:
        popup('Selecteer alleen PDF bestanden, of 1 PDF en 1 afbeelding.')

image = ImageTk.PhotoImage(Image.open(resource_path('images/logo-bokmerk.png')).resize((320, 96)))
logo = tk.Label(root, image = image)
logo.pack(side='top', pady=16)

style = ttk.Style()
style.theme_use('aqua')
style.configure(
    'TButton',
    background = 'white',
    foreground = '#16161D',
    width = 20,
    height = 1,
    borderwidth = 2
)

button = ttk.Button(root, text='Genereer', style='TButton', command=lambda: generate())
button.pack(side=tk.TOP, pady=20)

version_info = tk.Label(root, text="Versie 2.2")
version_info.pack(side='bottom', pady=16)

root.mainloop()
