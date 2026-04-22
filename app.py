import io
import os
import sys
import threading
import webbrowser
import qrcode
from flask import Flask, render_template, request, send_file, jsonify

# When running as a PyInstaller bundle, resolve the base path correctly
if getattr(sys, "frozen", False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=os.path.join(base_dir, "templates"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    url = request.form.get("url", "").strip()
    filename = request.form.get("filename", "").strip() or "qrcode"

    if not url:
        return jsonify({"error": "Please enter a URL."}), 400

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Sanitize filename
    filename = "".join(c for c in filename if c.isalnum() or c in "-_").strip() or "qrcode"
    if not filename.endswith(".png"):
        filename += ".png"

    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        return send_file(
            buf,
            mimetype="image/png",
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        return jsonify({"error": f"Failed to generate QR code: {str(e)}"}), 500


if __name__ == "__main__":
    port = 5000
    # Auto-open browser after a short delay
    threading.Timer(1.5, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)
