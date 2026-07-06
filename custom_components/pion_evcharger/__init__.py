"""
Custom integration to integrate Pion Power Elite EV chargers with Home Assistant.

For more details about this integration, please refer to
https://github.com/rosenqui/pion_power_evcharger
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from homeassistant.const import ATTR_DEVICE_ID, CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import ServiceCall, callback
from homeassistant.exceptions import InvalidStateError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry
from homeassistant.helpers.httpx_client import create_async_httpx_client
from homeassistant.loader import async_get_loaded_integration
from pion_power_api import PionPowerAPIClient

from .const import DEFAULT_URL, DOMAIN
from .coordinator import PionEvChargerDataUpdateCoordinator
from .data import PionEvChargerData, PionEvChargerDeviceData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import PionEvChargerConfigEntry

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


async def async_setup(hass: HomeAssistant, _config_entry: PionEvChargerConfigEntry) -> bool:
    """Set up is called when Home Assistant is loading our component."""

    @callback
    async def async_handle_start_charge(call: ServiceCall) -> None:
        """Handle the service action call."""
        coordinator = _get_coordinator_from_device(hass, call)
        device_data = cast("PionEvChargerDeviceData", coordinator.data)

        current = round(float(call.data.get("current") or 0))
        if current is None or current < 1:
            max_current = device_data.device_data.get("90100204")
            if max_current is None:
                msg = "Max current signal not found for device"
                raise InvalidStateError(msg)
            current = round(float(max_current.signal_value))

        duration = int(call.data.get("duration") or 24)
        if duration is None or duration < 1:
            msg = "Invalid duration provided"
            raise InvalidStateError(msg)

        await device_data.device.start_charging(current=current, duration_hours=duration)

    @callback
    async def async_handle_stop_charge(call: ServiceCall) -> None:
        """Handle the service action call."""
        coordinator = _get_coordinator_from_device(hass, call)
        device_data = cast("PionEvChargerDeviceData", coordinator.data)
        await device_data.device.stop_charging()

    hass.services.async_register(DOMAIN, "start_charge", async_handle_start_charge)
    hass.services.async_register(DOMAIN, "stop_charge", async_handle_stop_charge)

    # Return boolean to indicate that initialization was successful.
    return True


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
            username=config_entry.data[CONF_EMAIL],
            password=config_entry.data[CONF_PASSWORD],
            httpx_client=create_async_httpx_client(hass),
        ),
        integration=async_get_loaded_integration(hass, config_entry.domain),
        coordinator=coordinator,
    )

    # Save the coordinator in hass.data so that it can be accessed by other parts of the integration.
    hass.data.setdefault(DOMAIN, {})[config_entry.unique_id] = coordinator

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


def _get_coordinator_from_device(hass: HomeAssistant, call: ServiceCall) -> PionEvChargerDataUpdateCoordinator:
    """Get the coordinator associated with the device in the service call."""
    coordinators = list(hass.data[DOMAIN].keys())
    if len(coordinators) == 1:
        return hass.data[DOMAIN][coordinators[0]]

    device_entry = device_registry.async_get(hass).async_get(call.data[ATTR_DEVICE_ID])
    if not device_entry:
        msg = "Device not found in device registry"
        raise InvalidStateError(msg)
    config_entry_ids = device_entry.config_entries
    config_entry_id = next(
        (
            config_entry_id
            for config_entry_id in config_entry_ids
            if cast("PionEvChargerConfigEntry", hass.config_entries.async_get_entry(config_entry_id)).domain == DOMAIN
        ),
        None,
    )
    if not config_entry_id:
        msg = "Config entry not found for device"
        raise InvalidStateError(msg)
    entry = hass.config_entries.async_get_entry(config_entry_id)
    if not entry:
        msg = "Config entry not found"
        raise InvalidStateError(msg)
    config_entry_unique_id = entry.unique_id
    return hass.data[DOMAIN][config_entry_unique_id]
