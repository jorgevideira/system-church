from __future__ import annotations

from io import BytesIO


def build_qr_png(data: str) -> bytes:
    """Return a PNG QR code for *data*.

    We generate on-demand during email dispatch to avoid storing binary blobs in the DB.
    """
    import qrcode  # local import to keep startup lean

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(str(data or "").strip())
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

