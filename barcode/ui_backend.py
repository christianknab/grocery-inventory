from __future__ import annotations

import os
from dataclasses import dataclass

from operation import Operation
from esp32_ui_client import Esp32UiClient, Esp32UiClientConfig


def _normalize_header(header: Operation | str) -> str:
    if isinstance(header, Operation):
        return "ADDING" if header == Operation.INSERT else "REMOVING" if header == Operation.REMOVE else ""
    return str(header).strip().upper()


@dataclass(frozen=True)
class UiPayload:
    header: str | None = None
    body: str | None = None
    color: str | None = None


class DisplayBackend:
    def clear(self) -> None:
        raise NotImplementedError

    def set_display(self, *, header: Operation | str, body: str) -> None:
        raise NotImplementedError


class LedBackend:
    def update_leds(self, operation: Operation) -> None:
        raise NotImplementedError

    def blink_success(self, operation: Operation, times: int = 2, delay_s: float = 0.5) -> None:
        return

    def cleanup(self) -> None:
        return


class Esp32HttpDisplayBackend(DisplayBackend):
    def __init__(
        self,
        client: Esp32UiClient | None = None,
        config: Esp32UiClientConfig | None = None,
        logger=None,
    ):
        self._client = client or Esp32UiClient(config=config, logger=logger)

    def clear(self) -> None:
        # Explicit blank header/body.
        self._client.post_ui(header="", body="")

    def set_display(self, *, header: Operation | str, body: str) -> None:
        self._client.post_ui(header=_normalize_header(header), body=str(body))


class Esp32HttpLedBackend(LedBackend):
    def __init__(
        self,
        client: Esp32UiClient | None = None,
        config: Esp32UiClientConfig | None = None,
        logger=None,
    ):
        self._client = client or Esp32UiClient(config=config, logger=logger)

    def _operation_to_color(self, operation: Operation) -> str:
        return "GREEN" if operation == Operation.INSERT else "RED" if operation == Operation.REMOVE else ""

    def update_leds(self, operation: Operation) -> None:
        # LEDs are controlled by the ESP32 based on color.
        self._client.post_ui(color=self._operation_to_color(operation))


class LocalOledDisplayBackend(DisplayBackend):
    def __init__(self):
        try:
            import board  # type: ignore
            import adafruit_ssd1306  # type: ignore
            from PIL import Image, ImageDraw, ImageFont  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "Local OLED backend requires Raspberry Pi OLED libs (board, adafruit_ssd1306, Pillow). "
                "Either install them or set UI_BACKEND=http."
            ) from exc

        self._Image = Image
        self._ImageDraw = ImageDraw
        self._ImageFont = ImageFont

        self.WIDTH = 128
        self.HEIGHT = 64
        self.BORDER = 12
        self.HEADER_HEIGHT = 15

        i2c = board.I2C()
        self.oled = adafruit_ssd1306.SSD1306_I2C(self.WIDTH, self.HEIGHT, i2c, addr=0x3C)

        self.clear()

    def clear(self) -> None:
        self.oled.fill(0)
        self.oled.show()

    def set_display(self, *, header: Operation | str, body: str) -> None:
        Image = self._Image
        ImageDraw = self._ImageDraw
        ImageFont = self._ImageFont

        image = Image.new("1", (self.oled.width, self.oled.height))
        draw = ImageDraw.Draw(image)

        draw.rectangle((0, 0, self.oled.width, self.BORDER), outline=255, fill=255)
        font = ImageFont.load_default()

        header_text = _normalize_header(header)
        bbox = font.getbbox(header_text)
        font_width = bbox[2] - bbox[0]
        draw.text(
            (self.oled.width // 2 - font_width // 2, 0),
            header_text,
            font=font,
            fill=0,
        )

        draw.text(
            (0, self.HEADER_HEIGHT),
            str(body),
            font=font,
            fill=255,
        )

        self.oled.image(image)
        self.oled.show()


class LocalGpioLedBackend(LedBackend):
    def __init__(self, insert_pin: int, remove_pin: int):
        try:
            import RPi.GPIO as GPIO  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "Local GPIO backend requires RPi.GPIO. Either install it on a Pi or set UI_BACKEND=http."
            ) from exc

        import time

        self._GPIO = GPIO
        self._time = time

        self.insert_pin = insert_pin
        self.remove_pin = remove_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.insert_pin, GPIO.OUT)
        GPIO.setup(self.remove_pin, GPIO.OUT)
        self.off()

    def on(self, pin: int) -> None:
        self._GPIO.output(pin, self._GPIO.HIGH)

    def off(self, pin: int | None = None) -> None:
        if pin is not None:
            self._GPIO.output(pin, self._GPIO.LOW)
        else:
            self._GPIO.output(self.insert_pin, self._GPIO.LOW)
            self._GPIO.output(self.remove_pin, self._GPIO.LOW)

    def blink_success(self, operation: Operation, times: int = 2, delay_s: float = 0.5) -> None:
        pin = self.insert_pin if operation == Operation.INSERT else self.remove_pin
        for _ in range(times):
            self.off(pin)
            self._time.sleep(delay_s)
            self.on(pin)
            self._time.sleep(delay_s)

    def update_leds(self, operation: Operation) -> None:
        self.off()
        if operation == Operation.INSERT:
            self.on(self.insert_pin)
        elif operation == Operation.REMOVE:
            self.on(self.remove_pin)

    def cleanup(self) -> None:
        self._GPIO.cleanup()


def choose_backend(kind: str | None) -> str:
    if kind is None:
        kind = os.getenv("UI_BACKEND", "auto")
    kind = str(kind).strip().lower()
    return kind


def auto_select_display_backend() -> DisplayBackend:
    # Prefer local if it imports; else fallback to http.
    return Esp32HttpDisplayBackend()


def auto_select_led_backend(insert_pin: int | None, remove_pin: int | None) -> LedBackend:
    # try:
    #     if insert_pin is None or remove_pin is None:
    #         raise RuntimeError("pins missing")
    #     return LocalGpioLedBackend(insert_pin=insert_pin, remove_pin=remove_pin)
    # except Exception:
    return Esp32HttpLedBackend()
