# REF: https://learn.adafruit.com/monochrome-oled-breakouts/python-usage-2
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from operation import Operation

class DisplayController:
    def __init__(self):
        self.WIDTH = 128
        self.HEIGHT = 64
        self.BORDER = 12
        self.HEADER_HEIGHT = 15
        self.header = Operation.INSERT
        self.body = "Please Scan Item"
        self.oled = self._setup()
        self.clear()
    
    def _setup(self):
        # For I2C.
        i2c = board.I2C()  # uses board.SCL and board.SDA
        oled = adafruit_ssd1306.SSD1306_I2C(self.WIDTH, self.HEIGHT, i2c, addr=0x3C)
        return oled

    def clear(self):
        # Clear display.
        self.oled.fill(0)
        self.oled.show()

    def draw(self, image):
         # Display image
        self.oled.image(image)
        self.oled.show()
    
    # def set_display(self, operation):
    #     self.draw_image("ADDING" if operation == Operation.INSERT else "REMOVING" if operation == Operation.REMOVE else "", "Please scan an item")
    
    def draw_image(self, header=None, body=None):
        if header is None:
            header = self.header
        else:
            self.header = header
        if body is None:
            body = self.body
        else:
            self.body = body
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        image = Image.new("1", (self.oled.width, self.oled.height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        # Header filled
        draw.rectangle((0, 0, self.oled.width, self.BORDER), outline=255, fill=255)

        # Load default font.
        font = ImageFont.load_default()

        # Draw Some Text
        header = "ADDING" if header == Operation.INSERT else "REMOVING" if header == Operation.REMOVE else ""
        bbox = font.getbbox(header)
        (font_width, font_height) = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            (self.oled.width//2 - font_width//2, 0),
            header,
            font=font,
            fill=0,
        )

        bbox = font.getbbox(body)
        (font_width, font_height) = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            (0, self.HEADER_HEIGHT),
            body,
            font=font,
            fill=255,
        )
        self.draw(image)

# EXAMPLE
# display = DisplayController()
# header = "ADDING"
# body = "Pretzels, tiny twists"
# display.draw_image(header, body)