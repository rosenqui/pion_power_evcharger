"""Binary sensor platform for pion_evcharger."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory

from .entity import PionEvChargerEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import PionEvChargerDataUpdateCoordinator
    from .data import PionEvChargerConfigEntry, PionEvChargerDeviceData

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="90100000",
        name="Communication status",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinarySensorEntityDescription(
        key="90100002",
        name="Gun plugin status",
        device_class=BinarySensorDeviceClass.PLUG,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: PionEvChargerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    async_add_entities(
        PionEvChargerBinarySensor(coordinator=entry.runtime_data.coordinator, entity_description=entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class PionEvChargerBinarySensor(PionEvChargerEntity, BinarySensorEntity):
    """pion_evcharger binary_sensor class."""

    def __init__(
        self, coordinator: PionEvChargerDataUpdateCoordinator, entity_description: BinarySensorEntityDescription
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, entity_description.key)

        self.entity_description = entity_description

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        device_data = cast("PionEvChargerDeviceData", self.coordinator.data)
        signal = device_data.device_data.get(self._key)
        if signal:
            return float(signal.signal_value) != 0
        return False
