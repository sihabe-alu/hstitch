import io

from flask import Flask, Response, request, send_file
from PIL import Image, ImageOps, UnidentifiedImageError

app = Flask(__name__)


def stitch(files, fmt="png"):
    if not files:
        raise ValueError("no images")
    images = [ImageOps.exif_transpose(Image.open(f)) for f in files]
    width = sum(im.width for im in images)
    height = max(im.height for im in images)
    canvas = Image.new("RGB", (width, height), "white")
    x = 0
    for im in images:
        rgba = im.convert("RGBA")
        canvas.paste(rgba, (x, (height - im.height) // 2), rgba)
        x += im.width
    icc = images[0].info.get("icc_profile")
    out = io.BytesIO()
    if fmt == "jpeg":
        canvas.save(out, "JPEG", quality=100, subsampling=0, icc_profile=icc)
    else:
        canvas.save(out, "PNG", icc_profile=icc)
    return out.getvalue()


@app.get("/")
def index():
    return send_file("index.html")


@app.post("/stitch")
def stitch_route():
    fmt = "jpeg" if request.form.get("format") == "jpeg" else "png"
    try:
        data = stitch([f.stream for f in request.files.getlist("images")], fmt)
    except (ValueError, UnidentifiedImageError) as e:
        return Response(str(e), status=400, mimetype="text/plain")
    return Response(data, mimetype=f"image/{fmt}")
