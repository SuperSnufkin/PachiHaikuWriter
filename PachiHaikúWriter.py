import tkinter as tk
from tkinter import filedialog, messagebox
from reportlab.pdfgen import canvas as pdf_canvas
from odf.opendocument import OpenDocumentText
from odf.text import H, P
from PIL import Image, ImageDraw, ImageFont
import re
import os

def contar_silabas(palabra):
    palabra = palabra.lower()
    palabra = re.sub(r'[^a-záéíóúüñ]', '', palabra)
    silabas = re.findall(r'[aeiouáéíóúü]+', palabra)
    return len(silabas)

def contar_silabas_linea(linea):
    palabras = linea.strip().split()
    return sum(contar_silabas(p) for p in palabras)

class HaikuApp:
    def __init__(self, master):
        self.master = master
        master.title("PachiHaikúWriter")
        master.geometry("420x380")
        master.resizable(False, False)

        self.text_lines = []
        self.labels = []

        for i in range(3):
            label = tk.Label(master, text=f"Línea {i+1} (0 sílabas)")
            label.pack()
            self.labels.append(label)

            text = tk.Text(master, height=1, width=40, font=("Helvetica", 14))
            text.pack()
            text.bind("<KeyRelease>", self.actualizar_silabas)
            self.text_lines.append(text)

        # Firma del autor
        tk.Label(master, text="Firma del autor:").pack(pady=(10, 0))
        self.firma_text = tk.Text(master, height=1, width=40, font=("Helvetica", 14))
        self.firma_text.pack()

        self.validacion_label = tk.Label(master, text="", fg="red")
        self.validacion_label.pack(pady=5)

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)

        self.open_button = tk.Button(self.button_frame, text="Abrir", command=self.abrir_haiku)
        self.open_button.pack(side="left", padx=10)

        self.save_button = tk.Button(self.button_frame, text="Guardar", command=self.guardar_haiku)
        self.save_button.pack(side="left", padx=10)

        self.about_button = tk.Button(self.button_frame, text="Acerca de", command=self.mostrar_acerca_de)
        self.about_button.pack(side="left", padx=10)

    def actualizar_silabas(self, event=None):
        estructura = [5, 7, 5]
        es_valido = True
        for i, text in enumerate(self.text_lines):
            contenido = text.get("1.0", tk.END).strip()
            num_silabas = contar_silabas_linea(contenido)
            self.labels[i].config(text=f"Línea {i+1} ({num_silabas} sílabas)")
            if num_silabas != estructura[i]:
                es_valido = False

        if es_valido:
            self.validacion_label.config(text="✔ Haikú válido (estructura 5-7-5)", fg="green")
        else:
            self.validacion_label.config(text="✖ El haikú no cumple la estructura 5-7-5", fg="red")

    def abrir_haiku(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivo de texto", "*.txt")])
        if not file_path:
            return
        with open(file_path, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            for i in range(min(3, len(lineas))):
                self.text_lines[i].delete("1.0", tk.END)
                self.text_lines[i].insert(tk.END, lineas[i].strip())
            if len(lineas) > 3:
                self.firma_text.delete("1.0", tk.END)
                self.firma_text.insert(tk.END, lineas[3].strip())
            else:
                self.firma_text.delete("1.0", tk.END)
        self.actualizar_silabas()

    def guardar_haiku(self):
        file_path = filedialog.asksaveasfilename(
            title="Guardar haikú",
            filetypes=[
                ("PDF", "*.pdf"),
                ("Imagen PNG", "*.png"),
                ("Imagen JPG", "*.jpg"),
                ("Documento de texto (ODT)", "*.odt"),
            ],
            defaultextension=""
        )
        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            self.guardar_como_pdf(file_path)
        elif ext == ".odt":
            self.guardar_como_odt(file_path)
        elif ext in [".png", ".jpg", ".jpeg"]:
            formato = "PNG" if ext == ".png" else "JPEG"
            self.guardar_como_imagen(file_path, formato)
        else:
            messagebox.showerror("Error", "Por favor, escriba la extensión soportada al final del nombre:\n.pdf, .png, .jpg, .odt")

    def guardar_como_pdf(self, path):
        c = pdf_canvas.Canvas(path)
        c.setFont("Helvetica", 16)
        y = 750
        for text in self.text_lines:
            linea = text.get("1.0", tk.END).strip()
            c.drawString(100, y, linea)
            y -= 30
        firma = self.firma_text.get("1.0", tk.END).strip()
        if firma:
            c.setFont("Helvetica-Oblique", 12)
            c.drawString(100, y - 20, f"- {firma}")
        c.save()
        messagebox.showinfo("Guardado", f"Haikú guardado como PDF:\n{path}")

    def guardar_como_odt(self, path):
        doc = OpenDocumentText()
        doc.text.addElement(H(outlinelevel=1, text="Haikú"))
        for text in self.text_lines:
            linea = text.get("1.0", tk.END).strip()
            doc.text.addElement(P(text=linea))
        firma = self.firma_text.get("1.0", tk.END).strip()
        if firma:
            doc.text.addElement(P(text=f"- {firma}"))
        doc.save(path)
        messagebox.showinfo("Guardado", f"Haikú guardado como ODT:\n{path}")

    def guardar_como_imagen(self, path, formato):
        img = Image.new("RGB", (600, 600), "white")
        draw = ImageDraw.Draw(img)

        try:
            font_poema = ImageFont.truetype("DejaVuSans.ttf", 36)
            font_firma = ImageFont.truetype("DejaVuSans.ttf", 18)
        except:
            font_poema = ImageFont.load_default()
            font_firma = ImageFont.load_default()

        lineas = [text.get("1.0", tk.END).strip() for text in self.text_lines]
        firma = self.firma_text.get("1.0", tk.END).strip()

        # Calcular altura del poema
        alturas = [font_poema.getbbox(linea)[3] - font_poema.getbbox(linea)[1] for linea in lineas]
        espacio_entre_lineas = 15
        altura_total = sum(alturas) + espacio_entre_lineas * (len(lineas) - 1)
        y = (600 - altura_total) // 2

        for linea, alto in zip(lineas, alturas):
            bbox = draw.textbbox((0, 0), linea, font=font_poema)
            ancho = bbox[2] - bbox[0]
            x = (600 - ancho) // 2
            draw.text((x, y), linea, fill="black", font=font_poema)
            y += alto + espacio_entre_lineas

        if firma:
            bbox_firma = draw.textbbox((0, 0), firma, font=font_firma)
            ancho_firma = bbox_firma[2] - bbox_firma[0]
            alto_firma = bbox_firma[3] - bbox_firma[1]
            x_firma = 20
            y_firma = 600 - alto_firma - 20
            draw.text((x_firma, y_firma), f"- {firma}", fill="black", font=font_firma)

        img.save(path, formato)
        messagebox.showinfo("Guardado", f"Haikú guardado como {formato}:\n{path}")

    def mostrar_acerca_de(self):
        messagebox.showinfo(
            "Acerca de",
            "PachiHaikúWriter\n"
            "Programa creado por Israel G Bistrain y Pachi. Síguenos en Mastodon: @supersnufkin@mastodon.social\n"
            "Estructura: 5-7-5 sílabas.\n"
            "Formatos soportados: PDF, PNG, JPG, ODT\n\n"
            "IMPORTANTE:\n"
            "- Para guardar, agrega manualmente la extensión deseada al final del nombre del archivo (ej: mi_haiku.pdf)\n"
            "- Puedes firmar tu haikú en el campo inferior."
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = HaikuApp(root)
    root.mainloop()
