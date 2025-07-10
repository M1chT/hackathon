import base64
import cv2
import numpy as np
from PIL import Image as PILImage
import io


def detect_placeholder_box_from_b64(image_b64: str) -> tuple[int, int, int, int]:
    """
    Decode a Base64-encoded image and detect the placeholder rectangle:
    1) Decode Base64 to bytes
    2) Convert bytes to NumPy array and cv2.imdecode
    3) Canny-edge detect + dilate
    4) Find contours, approximate quads in bottom half, pick largest
    Returns (x, y, w, h)
    """
    # 1) Decode Base64 and load image
    img_data = base64.b64decode(image_b64)
    arr = np.frombuffer(img_data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Failed to decode image from Base64")

    # 2) Convert to gray and detect edges
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

    # 3) Find contours
    cnts, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    H, W = gray.shape
    best = (0, 0, 0, 0, 0)  # area, x, y, w, h

    for c in cnts:
        area = cv2.contourArea(c)
        if area < (W * H * 0.01):
            continue
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            if y > H * 0.4 and area > best[0]:
                best = (area, x, y, w, h)

    if best[0] == 0:
        raise RuntimeError("Placeholder rectangle not found.")
    _, x, y, w, h = best
    return x, y, w, h


def replace_qr_in_placeholder_from_b64(
    placeholder_b64: str, qr_path: str = "qr_placeholder/product_link.png"
) -> str:
    """
    Given Base64 of placeholder image and a filepath to QR image:
    1) Detect placeholder box from Base64 input.
    2) Decode placeholder to PIL Image.
    3) Load QR image from file path, resize to placeholder size.
    4) Paste QR over placeholder, then return final image as Base64 PNG.
    """
    print("Replacing QR in placeholder...")

    # Decode placeholder and detect coords
    x, y, w, h = detect_placeholder_box_from_b64(placeholder_b64)

    # Decode placeholder to PIL
    ph_data = base64.b64decode(placeholder_b64)
    base = PILImage.open(io.BytesIO(ph_data)).convert("RGBA")

    # Load QR from file path
    upload_folder = f"mcp_server/tools/{qr_path}"
    qr = PILImage.open(upload_folder).convert("RGBA")
    qr_resized = qr.resize((w, h), PILImage.LANCZOS)

    # Paste QR and encode
    base.paste(qr_resized, (x, y), qr_resized)
    buf = io.BytesIO()
    base.save(buf, format="PNG")

    print("Replacement successful...")
    return base64.b64encode(buf.getvalue()).decode("utf-8")
