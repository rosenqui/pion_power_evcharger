"""Constants for pion_evcharger."""

from logging import Logger, getLogger
from typing import Final

LOGGER: Logger = getLogger(__package__)

CONF_PION_DEVICE_CODE: Final = "pion_device_code"

DOMAIN: Final = "pion_evcharger"
DEFAULT_URL: Final = "https://evcharger.pionpower.ca/hems"
DEFAULT_SCAN_INTERVAL: int = 1
