# import random
# import string
# from PIL import Image, ImageDraw, ImageFont
# from io import BytesIO
# import base64

# def generate_captcha_text(length=5):
#     return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# def generate_captcha_image(text):
#     image = Image.new('RGB', (120, 40), color=(255, 255, 255))
#     font = ImageFont.load_default()
#     draw = ImageDraw.Draw(image)
#     draw.text((10, 5), text, font=font, fill=(0, 0, 0))

#     buffer = BytesIO()
#     image.save(buffer, format='PNG')
#     image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
#     return image_data



import random
import string
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import base64
import os

def generate_captcha_text(length=6):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

def generate_captcha_image(text):
    width, height = 150, 50
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Load a TTF font (use an available font on your system)
    font_path = "C:\\Windows\\Fonts\\Arial.ttf"
    font = ImageFont.truetype(font_path, 32)

    # Add background noise lines
    for _ in range(8):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)), width=2)

    # Add CAPTCHA text
    for i, char in enumerate(text):
        x = 10 + i * 20 + random.randint(-5, 5)
        y = random.randint(0, 10)
        draw.text((x, y), char, font=font, fill=(random.randint(0, 100), 0, 0))

    # Add random dots
    for _ in range(250):
        draw.point((random.randint(0, width), random.randint(0, height)), fill='gray')

    # Optionally apply filter for slight blur/distortion
    image = image.filter(ImageFilter.SMOOTH)

    # Encode image as base64
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return image_data



# import random
# import string
# from PIL import Image, ImageDraw, ImageFont, ImageFilter
# from io import BytesIO
# import base64
# import math

# def generate_captcha_text(length=5):
#     return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# def _wave_distort(image):
#     """Apply a sinusoidal wave distortion to the image."""
#     amplitude = 5
#     period = 30
#     width, height = image.size
#     new_image = Image.new("RGB", (width, height), (255, 255, 255))
#     pixels = new_image.load()
#     src_pixels = image.load()

#     for y in range(height):
#         offset = int(amplitude * math.sin(2 * math.pi * y / period))
#         for x in range(width):
#             new_x = x + offset
#             if 0 <= new_x < width:
#                 pixels[x, y] = src_pixels[new_x, y]
#             else:
#                 pixels[x, y] = (255, 255, 255)
#     return new_image

# def generate_captcha_image(text):
#     width = 150
#     height = 60
#     image = Image.new('RGB', (width, height), (255, 255, 255))

#     font_path = "C:\\Windows\\Fonts\\Arial.ttf"  # Adjust for your system
#     font_size = 40
#     font = ImageFont.truetype(font_path, font_size)

#     draw = ImageDraw.Draw(image)

#     # Draw random lines as noise
#     for _ in range(5):
#         start = (random.randint(0, width), random.randint(0, height))
#         end = (random.randint(0, width), random.randint(0, height))
#         line_color = (random.randint(0, 150), random.randint(0, 150), random.randint(0, 150))
#         draw.line([start, end], fill=line_color, width=2)

#     # Draw the captcha characters with random rotation & position
#     for i, char in enumerate(text):
#         x = 6 + i * 20 + random.randint(-3, 3)
#         y = random.randint(0, 15)
#         char_image = Image.new('RGBA', (40, 50), (255, 255, 255, 0))
#         char_draw = ImageDraw.Draw(char_image)
#         char_color = (random.randint(0, 50), random.randint(0, 50), random.randint(0, 50))
#         char_draw.text((0, 0), char, font=font, fill=char_color)

#         # Rotate character randomly between -30 and 30 degrees
#         rotated = char_image.rotate(random.uniform(-30, 30), resample=Image.BICUBIC, expand=1)

#         image.paste(rotated, (x, y), rotated)

#     # Add dots noise
#     for _ in range(50):
#         dot_x = random.randint(0, width)
#         dot_y = random.randint(0, height)
#         dot_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
#         draw.point((dot_x, dot_y), fill=dot_color)

#     # Apply wave distortion
#     image = _wave_distort(image)

#     # Apply filter to smooth a bit
#     image = image.filter(ImageFilter.SMOOTH_MORE)

#     buffer = BytesIO()
#     image.save(buffer, format='PNG')
#     image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
#     return image_data


