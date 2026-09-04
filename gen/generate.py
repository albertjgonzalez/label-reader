from barcode import Code128
from barcode.writer import ImageWriter
from datetime import date
from PIL import Image, ImageDraw, ImageText, ImageFont
from pathlib import Path

#Create data structure
barcode_string = '100000011111'
part_id_string = '200000022222'
image_date = date(2026, 9, 4)

image_elements = {
    "barcode": {
        "value": barcode_string,
        "coords": {"x1": 57, "y1": 200},
    },
    "partId": {
        "value": part_id_string,
        "coords": {"x1": 57, "y1": 100},
    },
    "date": {
        "value": image_date,
        "coords": {"x1": 57, "y1": 50},
    },
}

def placeImageOnCanvas(canvas, img, coords):
    canvas.paste(img, (coords["x1"], coords["y1"]))
    coords["x2"] = coords["x1"] + img.width
    coords["y2"] = coords["y1"] + img.height

#create canvas
canvas = Image.new('RGB',(400,400), (255,255,255))

#create barcode and add to canvas
barcode_image = Code128(barcode_string, writer=ImageWriter()).render({
    "module_width" : 0.2,
    "module_height": 5.0,
    "font_size": 8,
    "quiet_zone": 2.0,
    "write_text": True,
})

placeImageOnCanvas(canvas, barcode_image, image_elements["barcode"]["coords"])

#create partId and add to canvas
FONT_DIR = Path(__file__).parent / "fonts"
font = ImageFont.truetype(FONT_DIR / "DejaVuSansMono.ttf", 24)

part_id_text = ImageText.Text(part_id_string, font)
part_id_text.embed_color()

part_id_text_image = Image.new("RGB", part_id_text.get_bbox()[2:], (255,255,255))
part_id_text_image_draw = ImageDraw.Draw(part_id_text_image)
part_id_text_image_draw.text((0, 0), part_id_text, "black")

placeImageOnCanvas(canvas, part_id_text_image, image_elements["partId"]["coords"])

#create date and add to canvas
date_string = str(image_date)
date_string_text = ImageText.Text(date_string, font)
date_string_text.embed_color()

date_string_text_image = Image.new("RGB", date_string_text.get_bbox()[2:], (255,255,255))
date_string_text_image_draw = ImageDraw.Draw(date_string_text_image)
date_string_text_image_draw.text((0, 0), date_string_text, "black")

placeImageOnCanvas(canvas, date_string_text_image, image_elements["date"]["coords"])

canvas.save("renderedImg.png")