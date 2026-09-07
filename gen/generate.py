from barcode import Code128, Code39
from barcode.writer import ImageWriter
from datetime import date
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import cv2
from pylibdmtx.pylibdmtx import encode
import json
import segno
import zxingcpp
from io import BytesIO
import random
import numpy as np

def placeImageOnCanvas(canvas, img, field, x, y):
    canvas.paste(img, (x, y))
    field["quad"] = [(x, y),
    (x + img.width, y),
    (x + img.width, y + img.height),
    (x, y + img.height)]

def getCanvasHeight(fields, margin, gap):
    total_height = 0
    for field in fields:
        if field["image"] is None:
            continue
        total_height += field["image"].height
    return total_height + 2*margin + (gap * (len(fields) - 1))

def getCanvasWidth(fields, margin):
    max_width = 0
    for field in fields:
        if field["image"] is None:
            continue
        if field["image"].width > max_width:
            max_width = field["image"].width
    return 2*margin + max_width

def makeValueForRole(role):
    if role == "serial":
        return makeSerialNumber()
    elif role == "part_number":
        return makePartNumber()
    elif role == "model_number":
        return makeModelNumber()
    elif role == "lot_number":
        return makeLotNumber()
    elif role == "date":
        return makeDate()
    return None

def makeLabelFields():
    count = random.randint(1, 5)
    roles = ["serial"] + random.sample(["part_number", "model_number", "lot_number", "date"], count - 1)
    label_fields = []
    for role in roles:
        label_fields.append({
            "role": role, 
            "prefix": random.choice(["S/N", "SN", "SERIAL"])
                        if role == "serial" and random.choice([True, False]) else None,
            "value": makeValueForRole(role),
            "symbology": random.choice(["code128", 
                                        "code39", 
                                        "datamatrix",
                                        "qr",
                                        "text"]),
            "quad" : [],
        })
    random.shuffle(label_fields)
    return label_fields

def makeSerialNumber():
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    length = random.randint(10, 14)
    return ''.join(random.choice(chars) for _ in range(length))

def makePartNumber():
    groups = []
    for _ in range(3):
        groups.append(str(random.randint(1000, 9999)))
    return 'PN-' + '-'.join(groups)

def makeModelNumber():
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    digits = '0123456789'
    num_letters = random.randint(2, 3)
    num_digits = random.randint(3, 4)
    return ''.join(random.choice(letters) for _ in range(num_letters)) + ''.join(random.choice(digits) for _ in range(num_digits))

def makeLotNumber():
    return 'L' + str(random.randint(100000, 999999))

def makeDate():
    return str(date(random.randint(2020, 2030), random.randint(1, 12), random.randint(1, 28)))

def renderField(field):
    if field["symbology"] == "qr":
        return createQRImage(field["value"])
    if field["symbology"] == "code128":
        return createCode128Image(field["value"])
    elif field["symbology"] == "code39":
        return createCode39Image(field["value"])
    elif field["symbology"] == "datamatrix":
        return createDatamatrixImage(field["value"])
    elif field["symbology"] == "text":
        return createTextImage(field["value"])
    return None

def createQRImage(value):
    qr_string = value
    qr_image = segno.make(qr_string, micro=False)
    #qr_image.save("qr_code.png", scale=4)
    qr_image_bytes = BytesIO()
    qr_image.save(qr_image_bytes, kind="PNG", scale=4)
    qr_image_pil = Image.open(qr_image_bytes)
    return qr_image_pil

def createCode128Image(value):
    code128_string = value
    code128_image = Code128(code128_string, writer=ImageWriter()).render({
        "module_width" : 0.2,
        "module_height": 5.0,
        "font_size": 8,
        "quiet_zone": 2.0,
        "write_text": True,
    })
    return code128_image

def createCode39Image(value):
    code39_string = value
    code39_image = Code39(code39_string, writer=ImageWriter(), add_checksum=False).render({
        "module_width" : 0.2,
        "module_height": 5.0,
        "font_size": 8,
        "quiet_zone": 2.0,
        "write_text": True,
    })
    return code39_image

def createDatamatrixImage(value):
    datamatrix_string = value
    datamatrix_image_bytes = encode(datamatrix_string.encode())
    datamatrix_image = Image.frombytes("RGB", (datamatrix_image_bytes.width, datamatrix_image_bytes.height), datamatrix_image_bytes.pixels)
    return datamatrix_image

FONT_DIR = Path(__file__).parent / "fonts"
font = ImageFont.truetype(FONT_DIR / "DejaVuSansMono.ttf", 24)

def createTextImage(value):
    text_image = Image.new("RGB", font.getbbox(value)[2:], (255, 255, 255))
    draw = ImageDraw.Draw(text_image)
    draw.text((0, 0), value, font=font, fill="black")
    return text_image

def addPrefixToSerialImage(serialImage, prefix, gap):
    prefix_image = createTextImage(prefix)
    canvas = Image.new("RGB", (prefix_image.width 
                               + serialImage.width 
                               + gap, max(prefix_image.height, serialImage.height)), (255, 255, 255))
    canvas.paste(prefix_image, (0, (canvas.height - prefix_image.height)//2))
    canvas.paste(serialImage, ((prefix_image.width + gap), 0))
    return canvas

def rotateCanvas(canvas, labelFields):
    angle = random.uniform(0, 360)
    rotation_matrix = cv2.getRotationMatrix2D((canvas.width//2, canvas.height//2), angle, 1)
    rotated_canvas = cv2.warpAffine(np.array(canvas), rotation_matrix, (canvas.width, canvas.height))
    canvas = Image.fromarray(rotated_canvas)
    return canvas

margin = 20
gap = 15

labelFields = makeLabelFields()
for field in labelFields:
    field["image"] = renderField(field)
    if field["role"] == "serial" and field.get("prefix") is not None:
        field["image"] = addPrefixToSerialImage(field["image"], field["prefix"], gap)

#create canvas calculate size and add images
canvasHeight = getCanvasHeight(labelFields, margin, gap)
canvasWidth = getCanvasWidth(labelFields, margin)

canvas = Image.new('RGB',(canvasWidth,canvasHeight), (255,255,255))

y = margin
for field in labelFields:
    if field["image"] is None:
        continue
    placeImageOnCanvas(canvas, field["image"], field, margin, y)
    y += field["image"].height + gap

canvas = rotateCanvas(canvas, labelFields)
canvas.save("renderedImg.png")

#create data json
ground_truth = []
for field in labelFields:
    ground_truth.append({
        "role": field["role"],
        "symbology": field["symbology"],
        "value": str(field["value"]),
        "prefix": field["prefix"],
        "quad": field["quad"]
    })
data_json = json.dumps(ground_truth)
with open("renderedImg.json", "w") as f:
    f.write(data_json)
    f.write("\n")

#use zxing to readbarcodes
# for name, img in [("code128", barcode_image), ("code39", code39_image),
#                   ("qr", qr_image_pil), ("datamatrix", datamatrix_image)]:
#         for r in zxingcpp.read_barcodes(img):
#             print(name, r.text, r.format, r.position)
