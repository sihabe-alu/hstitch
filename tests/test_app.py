import io

from PIL import Image

from app import app


def png(size, color):
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, "PNG")
    buf.seek(0)
    return buf


def post(client, files, **data):
    return client.post(
        "/stitch",
        data={"images": [(f, "x.png") for f in files], **data},
        content_type="multipart/form-data",
    )


def test_stitch_route_returns_png_by_default():
    r = post(app.test_client(), [png((10, 20), "red"), png((10, 30), "blue")])
    assert r.status_code == 200
    assert r.mimetype == "image/png"
    assert Image.open(io.BytesIO(r.data)).size == (20, 30)


def test_jpeg_format():
    r = post(app.test_client(), [png((8, 8), "red")], format="jpeg")
    assert r.mimetype == "image/jpeg"


def test_unknown_format_falls_back_to_png():
    r = post(app.test_client(), [png((8, 8), "red")], format="bmp")
    assert r.status_code == 200
    assert r.mimetype == "image/png"


def test_corrupt_upload_is_400():
    r = post(app.test_client(), [io.BytesIO(b"junk")])
    assert r.status_code == 400


def test_no_files_is_400():
    r = post(app.test_client(), [])
    assert r.status_code == 400
