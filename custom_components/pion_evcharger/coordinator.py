"""DataUpdateCoordinator for pion_evcharger."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.const import (
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import DOMAIN, HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pion_power_api import PionAuthError, PionConnectionError, PionLoginError

from .const import CONF_PION_DEVICE_CODE, DEFAULT_SCAN_INTERVAL, LOGGER

if TYPE_CHECKING:
    from .data import PionEvChargerConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class PionEvChargerDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, config_entry: PionEvChargerConfigEntry) -> None:
        """Initialize."""
        self.scan_interval: int = config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL) * 60

        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=self.scan_interval),
            always_update=False,  # Only update if data has changed.
        )

    config_entry: PionEvChargerConfigEntry

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            api_client = self.config_entry.runtime_data.client

            if not api_client.is_logged_in:
                await api_client.login()
            device = await api_client.get_device(str(self.config_entry.data.get(CONF_PION_DEVICE_CODE)))
            device_data = await device.get_realtime_data()
            device_stats = await device.get_stats()
        except PionLoginError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except PionAuthError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except PionConnectionError as exception:
            raise UpdateFailed(exception) from exception
        else:
            return {"device": device, "device_data": device_data, "device_stats": device_stats}
