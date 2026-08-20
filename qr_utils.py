import hmac
import hashlib
import qrcode
from io import BytesIO

SECRET = "traceqr-secret-key"

# CHANGE THIS to your laptop's IPv4 address
BASE_URL = "http://192.168.1.38:8501"


def sign(product_id: str) -> str:
    return hmac.new(
        SECRET.encode(),
        product_id.encode(),
        hashlib.sha256
    ).hexdigest()[:10]


def verify_signature(product_id: str, sig: str) -> bool:
    return hmac.compare_digest(
        sign(product_id),
        sig
    )


def generate_qr_image(product_id: str):
    # Create signature
    sig = sign(product_id)

    # Create URL that the phone will open
    url = f"{BASE_URL}/Verify_Product?id={product_id}&sig={sig}"

    # Generate QR
    img = qrcode.make(url)

    # Convert PIL Image → PNG bytes
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    return buffer.getvalue()