import io

from PIL import Image, ImageOps


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
