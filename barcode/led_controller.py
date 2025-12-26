from __future__ import annotations

from operation import Operation
from esp32_ui_client import Esp32UiClient, Esp32UiClientConfig
from ui_backend import (
    LedBackend,
    Esp32HttpLedBackend,
    LocalGpioLedBackend,
    auto_select_led_backend,
    choose_backend,
)

class LEDController:
    def __init__(
        self,
        insert_pin=None,
        remove_pin=None,
        backend: str | None = None,
        client: Esp32UiClient | None = None,
        config: Esp32UiClientConfig | None = None,
        logger=None,
        default_body: str = "Please Scan Item",
    ):
        # Pins retained for backward compatibility; unused with ESP32.
        self.insert_pin = insert_pin
        self.remove_pin = remove_pin
        self._body = default_body

        kind = choose_backend(backend)
        if kind == "local":
            if insert_pin is None or remove_pin is None:
                raise ValueError("local LED backend requires insert_pin and remove_pin")
            self._backend: LedBackend = LocalGpioLedBackend(insert_pin=insert_pin, remove_pin=remove_pin)
        elif kind == "http":
            self._backend = Esp32HttpLedBackend(client=client, config=config, logger=logger)
        else:
            self._backend = auto_select_led_backend(insert_pin=insert_pin, remove_pin=remove_pin)

    def set_body(self, body: str) -> None:
        self._body = str(body)

    def off(self, pin=None):
        # Keep legacy API; only meaningful for local GPIO backend.
        off = getattr(self._backend, "off", None)
        if callable(off):
            off(pin)

    def blink(self, pin, times, delay):
        # Keep legacy API; only meaningful for local GPIO backend.
        blink = getattr(self._backend, "blink", None)
        if callable(blink):
            blink(pin, times, delay)

    def blink_success(self, operation: Operation, times: int = 2, delay_s: float = 0.5) -> None:
        self._backend.blink_success(operation, times=times, delay_s=delay_s)

    def update_leds(self, operation):
        # For HTTP backend, operation controls both LEDs and display header.
        self._backend.update_leds(operation)

    def cleanup(self):
        self._backend.cleanup()