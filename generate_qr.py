import qrcode

url = "http://10.10.10.11:5000"   # use your exact address shown
qrcode.make(url).save("park_entry_form_qr.png")

print("QR code saved successfully!")