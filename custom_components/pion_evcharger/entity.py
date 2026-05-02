"""PionEvChargerEntity class."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import PionEvChargerDataUpdateCoordinator

if TYPE_CHECKING:
    from pion_power_api import Device


class PionEvChargerEntity(CoordinatorEntity[PionEvChargerDataUpdateCoordinator]):
    """PionEvChargerEntity class."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: PionEvChargerDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id

        device = cast("Device", coordinator.data.get("device"))

        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            manufacturer="Pion Power",  # TODO(rosenqui) get this from the Login response
            model=device.product_name if device else "Unknown Model",
            name=device.device_name if device else "Unknown Device",
            serial_number=device.device_code if device else "Unknown Serial",
            sw_version=device.software_version if device else "Unknown Software Version",
            hw_version=device.hardware_version if device else "Unknown Hardware Version",
            model_id=device.product_code if device else "Unknown Product Code",
        )
