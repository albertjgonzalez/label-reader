from barcode import Code128, Code39
from barcode.writer import ImageWriter
from datetime import date
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import cv2
from pylibdmtx.pylibdmtx import encode
import json
import segno
from io import BytesIO
import random
import numpy as np
import os

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

def rotateAndScaleCanvas(canvas, labelFields):
    angle = random.uniform(0, 360)
    rotation_matrix = cv2.getRotationMatrix2D((canvas.width//2, canvas.height//2), angle, random.uniform(0.7, 1.3))
    cos = abs(rotation_matrix[0,0])
    sin = abs(rotation_matrix[0,1])
    new_width = int(canvas.height * sin + canvas.width * cos)
    new_height = int(canvas.height * cos + canvas.width * sin)
    rotation_matrix[0,2] += new_width / 2 - canvas.width / 2
    rotation_matrix[1,2] += new_height / 2 - canvas.height / 2
    rotated_canvas = cv2.warpAffine(np.array(canvas), rotation_matrix, (new_width, new_height))
    canvas = Image.fromarray(rotated_canvas)
    for field in labelFields:
        new_quad = []
        for (x,y) in field["quad"]:
            new_x = rotation_matrix[0,0] * x + rotation_matrix[0,1] * y + rotation_matrix[0,2]
            new_y = rotation_matrix[1,0] * x + rotation_matrix[1,1] * y + rotation_matrix[1,2]
            new_quad.append((new_x, new_y))
        field["quad"] = new_quad
    return canvas

def alterCanvasPerspective(canvas, labelFields):
    points = np.float32([(0,0), (canvas.width,0), (canvas.width,canvas.height), (0,canvas.height)])
    jitter = canvas.width * 0.08
    new_points = np.float32([(points[i][0] + random.uniform(-jitter, jitter), points[i][1] + random.uniform(-jitter, jitter)) for i in range(4)])
    min_x = np.min(new_points[:,0])
    min_y = np.min(new_points[:,1])
    if min_x < 0:
        new_points[:,0] -= min_x
    if min_y < 0:
        new_points[:,1] -= min_y
    matrix = cv2.getPerspectiveTransform(points, new_points)
    out_height = int(max(new_points[:,1]))
    out_width = int(max(new_points[:,0]))
    warped = cv2.warpPerspective(np.array(canvas), matrix, (out_width, out_height))
    canvas = Image.fromarray(warped)
    for field in labelFields:
        new_quad = []
        for (x,y) in field["quad"]:
            w = matrix[2,0] * x + matrix[2,1] * y + matrix[2,2]
            new_x = (matrix[0,0] * x + matrix[0,1] * y + matrix[0,2]) / w
            new_y = (matrix[1,0] * x + matrix[1,1] * y + matrix[1,2]) / w
            new_quad.append((new_x, new_y))
        field["quad"] = new_quad
    return canvas

def makeBackground(height, width):
    noise = np.random.randint(60, 200, (height, width, 3), dtype=np.uint8)
    blurred = cv2.GaussianBlur(noise, (0,0), random.randint(15,25))
    background_image = Image.fromarray(blurred)
    return background_image

classList = ["code128",
             "code39",
             "datamatrix",
             "qr",
             "text"]

def writeYOLOFile(fields, image, path):
    lines = []
    for field in fields:
        i = classList.index(field["symbology"])
        coords = []
        for (x,y) in field["quad"]:
            coords.append(max(0, min(1.0, x / image.width)))
            coords.append(max(0,0, min(1.0, y / image.height)))
        lines.append(f"{i} {' '.join(map(str, coords))}")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    

#---------Create image 
def generateLabelImage(outDir, name):
    margin = 20
    gap = 15

    labelFields = makeLabelFields()
    for field in labelFields:
        field["image"] = renderField(field)
        if field["role"] == "serial" and field.get("prefix") is not None:
            field["image"] = addPrefixToSerialImage(field["image"], field["prefix"], gap)

    # create canvas calculate size and add images
    canvasHeight = getCanvasHeight(labelFields, margin, gap)
    canvasWidth = getCanvasWidth(labelFields, margin)

    canvas = Image.new('RGB', (canvasWidth, canvasHeight), (255, 255, 255))

    y = margin
    for field in labelFields:
        if field["image"] is None:
            continue
        placeImageOnCanvas(canvas, field["image"], field, margin, y)
        y += field["image"].height + gap

    # Manipulate the canvas randomly
    canvas = rotateAndScaleCanvas(canvas, labelFields)
    canvas = alterCanvasPerspective(canvas, labelFields)

    # Create background image and and add canvas to it
    background = makeBackground(int(canvas.height * 1.4), int(canvas.width * 1.4))
    offset_x = random.randint(0, int(background.width - canvas.width))
    offset_y = random.randint(0, int(background.height - canvas.height))
    background.paste(canvas, (offset_x, offset_y))

    for field in labelFields:
        field["quad"] = [(x + offset_x, y + offset_y) for (x, y) in field["quad"]]

    background.save(f"{outDir}/images/{name}.png")

    # create YOLO file
    writeYOLOFile(labelFields, background, f"{outDir}/labels/{name}.txt")

    # create data json
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
    with open(f"{outDir}/labels/{name}.json", "w") as f:
        f.write(data_json)
        f.write("\n")

def generateSplit(split, count, seed):
    random.seed(seed)
    np.random.seed(seed)
    os.makedirs(f"data/{split}/images", exist_ok=True)
    os.makedirs(f"data/{split}/labels", exist_ok=True)
    for i in range(count):
        generateLabelImage(f"data/{split}", f"{split}_{i:05d}")

manifest = {
    "splits" : {
        "train" : {"count" : 800, "seed" : 1},
        "val" : {"count" : 150, "seed" : 2},
        "test" : {"count" : 50, "seed" : 3}
    },
    "classes": classList,
    "margin" : 20,
    "gap" : 15,
}

for split, cfg in manifest["splits"].items():
    generateSplit(split, cfg["count"], cfg["seed"])

with open(f"data/manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)
    

#use zxing to readbarcodes
# for name, img in [("code128", barcode_image), ("code39", code39_image),
#                   ("qr", qr_image_pil), ("datamatrix", datamatrix_image)]:
#         for r in zxingcpp.read_barcodes(img):
#             print(name, r.text, r.format, r.position)
