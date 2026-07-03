import qrcode
import io
from pathlib import Path

def generate_qr_code(url, filename=None):
    """
    Generate a QR code image for the given URL.
    
    Args:
        url: The URL to encode in the QR code
        filename: Optional filename to save the QR code. If None, returns BytesIO buffer.
    
    Returns:
        Path to saved file or BytesIO buffer if no filename provided
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    if filename:
        img.save(filename)
        return Path(filename)
    else:
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer

# Generate QR code for the park entry form
if __name__ == "__main__":
    # Use the network IP address
    url = "http://10.10.10.5:5000"
    qr_path = generate_qr_code(url, "park_entry_form_qr.png")
    print(f"QR code saved successfully at: {qr_path}")
    print(f"QR code points to: {url}")