# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This demo will fill the screen with white, draw a black box on top
and then print Hello World! in the center of the display

This example is for use on (Linux) computers that are using CPython with
Adafruit Blinka to support CircuitPython libraries. CircuitPython does
not support PIL/pillow (python imaging library)!
"""

# REF: https://learn.adafruit.com/monochrome-oled-breakouts/python-usage-2
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

WIDTH = 128
HEIGHT = 64
BORDER = 15

# Use for I2C.
i2c = board.I2C()  # uses board.SCL and board.SDA
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)

# Clear display.
oled.fill(0)
oled.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("1", (oled.width, oled.height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a smaller inner rectangle
draw.rectangle((0, 0, oled.width, BORDER), outline=255, fill=255)

# Load default font.
font = ImageFont.load_default()

# Draw Some Text
text = "ADDING"
bbox = font.getbbox(text)
(font_width, font_height) = bbox[2] - bbox[0], bbox[3] - bbox[1]
draw.text(
    (0, 0),
    text,
    font=font,
    fill=0,
)

text = "blah blah blah!!!"
bbox = font.getbbox(text)
(font_width, font_height) = bbox[2] - bbox[0], bbox[3] - bbox[1]
draw.text(
    (0, BORDER),
    text,
    font=font,
    fill=255,
)

# Display image
oled.image(image)
oled.show()
