"""
Custom integration to integrate Pion Power Elite EV chargers with Home Assistant.

For more details about this integration, please refer to
https://github.com/rosenqui/pion_power_evcharger
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.loader import async_get_loaded_integration
from pion_power_api import PionPowerAPIClient

from .const import DEFAULT_URL
from .coordinator import PionEvChargerDataUpdateCoordinator
from .data import PionEvChargerData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import PionEvChargerConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    # Platform.SWITCH,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: PionEvChargerConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = PionEvChargerDataUpdateCoordinator(hass=hass, config_entry=config_entry)
    config_entry.runtime_data = PionEvChargerData(
        client=PionPowerAPIClient(
            base_url=DEFAULT_URL,
            username=config_entry.data[CONF_USERNAME],
            password=config_entry.data[CONF_PASSWORD],
            httpx_client=get_async_client(hass),
        ),
        integration=async_get_loaded_integration(hass, config_entry.domain),
        coordinator=coordinator,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    config_entry.async_on_unload(config_entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: PionEvChargerConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: PionEvChargerConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
