import io

import pytest
from PIL import Image, UnidentifiedImageError

from app import stitch


def make(size, color, mode="RGB", fmt="PNG", **save_kw):
    buf = io.BytesIO()
    Image.new(mode, size, color).save(buf, fmt, **save_kw)
    buf.seek(0)
    return buf


def open_result(data):
    return Image.open(io.BytesIO(data))


def test_size_is_sum_of_widths_and_max_height():
    out = open_result(stitch([make((30, 20), "red"), make((10, 50), "blue")]))
    assert out.size == (40, 50)


def test_png_is_lossless_and_centered_with_white_padding():
    out = open_result(stitch([make((30, 20), (255, 0, 0)), make((10, 50), (0, 0, 255))])).convert("RGB")
    assert out.getpixel((0, 15)) == (255, 0, 0)      # red starts at y=(50-20)//2=15
    assert out.getpixel((29, 34)) == (255, 0, 0)
    assert out.getpixel((0, 0)) == (255, 255, 255)   # padding above red
    assert out.getpixel((0, 49)) == (255, 255, 255)  # padding below red
    assert out.getpixel((30, 0)) == (0, 0, 255)      # blue fills full height


def test_jpeg_output():
    out = open_result(stitch([make((8, 8), "red"), make((8, 8), "blue")], "jpeg"))
    assert out.format == "JPEG"


def test_exif_rotation_is_applied():
    exif = Image.Exif()
    exif[0x0112] = 6  # rotate 90 CW when displayed
    rotated = make((40, 10), "red", fmt="JPEG", exif=exif.tobytes())
    out = open_result(stitch([rotated, make((5, 5), "blue")]))
    assert out.size == (10 + 5, 40)


def test_transparent_png_padding_is_white_not_black():
    clear = make((10, 10), (0, 0, 0, 0), mode="RGBA")
    out = open_result(stitch([clear, make((10, 10), "blue")])).convert("RGB")
    assert out.getpixel((5, 5)) == (255, 255, 255)


@pytest.mark.parametrize("mode,color", [("P", 3), ("L", 128)])
def test_non_rgb_modes(mode, color):
    out = open_result(stitch([make((6, 6), color, mode=mode), make((6, 9), "blue")]))
    assert out.size == (12, 9)


def test_corrupt_file_raises():
    with pytest.raises(UnidentifiedImageError):
        stitch([io.BytesIO(b"not an image")])


def test_empty_raises_value_error():
    with pytest.raises(ValueError):
        stitch([])


def test_large_photos_are_not_rejected_as_decompression_bombs():
    assert Image.MAX_IMAGE_PIXELS is None
