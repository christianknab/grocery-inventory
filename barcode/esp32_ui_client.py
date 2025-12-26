import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Esp32UiClientConfig:
    base_url: str
    display_path: str
    timeout_s: float = 2.0
    retries: int = 1
    retry_backoff_s: float = 0.25

    @staticmethod
    def from_env(
        base_url_env: str = "ESP32_BASE_URL",
        display_path_env: str = "ESP32_DISPLAY_PATH",
        timeout_env: str = "ESP32_TIMEOUT_S",
        retries_env: str = "ESP32_RETRIES",
        backoff_env: str = "ESP32_RETRY_BACKOFF_S",
        default_base_url: str = "",
    ) -> "Esp32UiClientConfig":
        base_url = os.getenv(base_url_env, default_base_url).rstrip("/")
        display_path = os.getenv(display_path_env, "")
        timeout_s = float(os.getenv(timeout_env, "2.0"))
        retries = int(os.getenv(retries_env, "1"))
        retry_backoff_s = float(os.getenv(backoff_env, "0.25"))
        return Esp32UiClientConfig(
            base_url=base_url,
            display_path=display_path,
            timeout_s=timeout_s,
            retries=retries,
            retry_backoff_s=retry_backoff_s,
        )


class Esp32UiClient:
    def __init__(self, config: Optional[Esp32UiClientConfig] = None, logger=None):
        self.config = config or Esp32UiClientConfig.from_env()
        self.logger = logger

    def set_display(self, header: str, body: str) -> None:
        url = f"{self.config.base_url}{self.config.display_path}"
        payload = {"header": header, "body": body}
        self._post_json(url, payload)

    def _post_json(self, url: str, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        last_exc: Optional[BaseException] = None
        attempts = max(1, self.config.retries)
        for attempt in range(1, attempts + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.config.timeout_s) as resp:
                    resp.read()  # drain
                return
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
                last_exc = exc
                if self.logger:
                    self.logger.warning(
                        f"ESP32 UI POST failed (attempt {attempt}/{attempts}) to {url}: {exc}"
                    )
                if attempt < attempts:
                    time.sleep(self.config.retry_backoff_s)

        if self.logger:
            self.logger.error(f"ESP32 UI POST ultimately failed to {url}: {last_exc}")
