from PIL import Image, ImageDraw, ImageFont
import os

# Create a clean institutional badge for Polícia Federal
width = 400
height = 480
image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Colors from Frontline PF
gold = (225, 173, 98, 255)       # PF-Gold500 #E1AD62
gold_dark = (193, 149, 21, 255)  # PF-Gold600
gold_deep = (133, 100, 4, 255)   # PF-Gold700
black = (17, 18, 19, 255)        # PF-Black #111213
blue = (51, 99, 204, 255)        # PF-Blue500 #3363CC
white = (255, 255, 255, 255)

# Outer Shield Coordinates
shield_points = [
    (200, 20),   # Top point
    (360, 40),   # Top right
    (380, 240),  # Mid right
    (200, 460),  # Bottom point
    (20, 240),   # Mid left
    (40, 40),    # Top left
]

# Draw Outer Gold Border
draw.polygon(shield_points, fill=black, outline=gold, width=8)

# Inner Shield
inner_shield = [
    (200, 40),
    (340, 58),
    (360, 235),
    (200, 440),
    (40, 235),
    (60, 58),
]
draw.polygon(inner_shield, fill=black, outline=gold_dark, width=3)

# Central Star / Sun rays
center_x, center_y = 200, 210
draw.ellipse([center_x - 90, center_y - 90, center_x + 90, center_y + 90], outline=gold, width=4)
draw.ellipse([center_x - 70, center_y - 70, center_x + 70, center_y + 70], fill=blue, outline=gold, width=3)

# 5-pointed star in center
import math
star_points = []
for i in range(10):
    r = 55 if i % 2 == 0 else 24
    angle = i * math.pi / 5 - math.pi / 2
    x = center_x + int(r * math.cos(angle))
    y = center_y + int(r * math.sin(angle))
    star_points.append((x, y))
draw.polygon(star_points, fill=gold, outline=white, width=1)

# Institutional text on top banner
banner_points = [
    (70, 75),
    (330, 75),
    (310, 115),
    (90, 115)
]
draw.polygon(banner_points, fill=gold, outline=gold_deep, width=2)

# Text: POLICIA FEDERAL
try:
    font = ImageFont.truetype("arial.ttf", 22)
    font_small = ImageFont.truetype("arial.ttf", 16)
    font_bold = ImageFont.truetype("arialbd.ttf", 20)
except Exception:
    font = ImageFont.load_default()
    font_small = font
    font_bold = font

draw.text((115, 82), "POLÍCIA FEDERAL", fill=black, font=font_bold)
draw.text((120, 360), "ORDEM E PROGRESSO", fill=gold, font=font_small)

os.makedirs('static/img', exist_ok=True)
image.save('static/img/brasao_pf.png', 'PNG')
print("Successfully generated static/img/brasao_pf.png")
