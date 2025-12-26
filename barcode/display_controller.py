from __future__ import annotations

from operation import Operation
from esp32_ui_client import Esp32UiClient, Esp32UiClientConfig
from ui_backend import (
    DisplayBackend,
    Esp32HttpDisplayBackend,
    LocalOledDisplayBackend,
    auto_select_display_backend,
    choose_backend,
)

class DisplayController:
    def __init__(
        self,
        backend: str | None = None,
        client: Esp32UiClient | None = None,
        config: Esp32UiClientConfig | None = None,
        logger=None,
        default_header: Operation | str = Operation.INSERT,
        default_body: str = "Please Scan Item",
    ):
        self.header = default_header
        self.body = default_body
        kind = choose_backend(backend)
        if kind == "local":
            self._backend: DisplayBackend = LocalOledDisplayBackend()
        elif kind == "http":
            self._backend = Esp32HttpDisplayBackend(client=client, config=config, logger=logger)
        else:
            self._backend = auto_select_display_backend()

    def clear(self):
        self._backend.clear()

    def draw_image(self, header=None, body=None):
        if header is None:
            header = self.header
        else:
            self.header = header
        if body is None:
            body = self.body
        else:
            self.body = body
        self._backend.set_display(header=header, body=str(body))

# EXAMPLE
# display = DisplayController()
# display.draw_image("ADDING", "Pretzels, tiny twists")