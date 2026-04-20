"""PionEvChargerEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import PionEvChargerDataUpdateCoordinator


class PionEvChargerEntity(CoordinatorEntity[PionEvChargerDataUpdateCoordinator]):
    """PionEvChargerEntity class."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: PionEvChargerDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            manufacturer="Pion Power",
            model=coordinator.config_entry.data.get("product_name", "Unknown Model"),
            name=coordinator.config_entry.data.get("device_name", "Unknown Device"),
            serial_number=coordinator.config_entry.data.get(
                "device_code", "Unknown Serial"
            ),
        )
