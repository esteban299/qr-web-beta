from flask import Flask, render_template, request, redirect
import qrcode
from PIL import Image
import io
import base64

app = Flask(__name__)

# Lista en memoria para guardar los códigos generados
lista_qrs = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        fill_color = request.form.get("fill_color", "#6366f1")
        back_color = request.form.get("back_color", "#ffffff")
        
        logo_file = request.files.get("logo")

        if url:
            # 1. Crear el código QR con alta corrección de errores
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4
            )
            qr.add_data(url)
            qr.make(fit=True)

            img = qr.make_image(fill_color=fill_color, back_color=back_color).convert('RGB')

            # 2. Pegar el logo si se subió uno
            if logo_file and logo_file.filename != '':
                logo = Image.open(logo_file)

                qr_w, qr_h = img.size
                logo_size = qr_w // 5
                logo = logo.resize((logo_size, logo_size))

                pos_x = (qr_w - logo_size) // 2
                pos_y = (qr_h - logo_size) // 2

                img.paste(logo, (pos_x, pos_y))

            # 3. Convertir a base64
            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)

            imagen_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

            # Guardar en la lista
            nuevo_qr = {
                "url": url,
                "imagen": imagen_base64
            }
            lista_qrs.append(nuevo_qr)

            return render_template("index.html", qr_creado=imagen_base64)

    return render_template("index.html")

@app.route("/soporte")
def soporte():
    return render_template("soporte.html")

@app.route("/mis-codigos")
def mis_codigos():
    return render_template("mis_codigos.html", codigos=lista_qrs)

@app.route("/eliminar-qr/<int:indice>", methods=["POST"])
def eliminar_qr(indice):
    if 0 <= indice < len(lista_qrs):
        lista_qrs.pop(indice)
    return redirect("/mis-codigos")

if __name__ == "__main__":
    app.run(debug=True)