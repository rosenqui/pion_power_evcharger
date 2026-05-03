"""PionEvChargerEntity class."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PionEvChargerDataUpdateCoordinator

if TYPE_CHECKING:
    from custom_components.pion_evcharger.data import PionEvChargerDeviceData


class PionEvChargerEntity(CoordinatorEntity[PionEvChargerDataUpdateCoordinator]):
    """PionEvChargerEntity class."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: PionEvChargerDataUpdateCoordinator, key: str) -> None:
        """Initialize."""
        super().__init__(coordinator)

        device = cast("PionEvChargerDeviceData", self.coordinator.data).device

        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            hw_version=device.hardware_version if device else "Unknown Hardware Version",
            manufacturer=device.client.company_code if device else "Pion Power",
            model_id=device.product_code if device else "Unknown Product Code",
            model=device.product_name if device else "Unknown Model",
            name=device.device_name if device else "Unknown Device",
            serial_number=device.device_code if device else "Unknown Serial",
            suggested_area="Garage",
            sw_version=device.software_version if device else "Unknown Software Version",
        )
        self._attr_unique_id = f"{DOMAIN}_{device.device_code}_{key}"
        self._key = key
