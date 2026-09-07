from PIL import Image, ImageDraw
import json

renderedImage = Image.open("renderedImg.png")
with open("renderedImg.json") as f:
    imageJson = json.load(f)

image_draw = ImageDraw.Draw(renderedImage)

for field in imageJson:
    quad = field["quad"]
    image_draw.polygon(quad, outline="red", width=2)
    image_draw.text((quad[0][0], quad[0][1]), field["value"], fill="red")

renderedImage.save("qc_overlay.png")