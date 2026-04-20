"""Sensor platform for pion_evcharger."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .entity import PionEvChargerEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import PionEvChargerDataUpdateCoordinator
    from .data import PionEvChargerConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="pion_station_code",
        name="Station Code",
        icon="mdi:identifier",
    ),
    SensorEntityDescription(
        key="pion_device_code",
        name="Device Code",
        icon="mdi:identifier",
    ),
    SensorEntityDescription(
        key="device_name",
        name="Device Name",
        icon="mdi:identifier",
    ),
    SensorEntityDescription(
        key="product_name",
        name="Product Name",
        icon="mdi:identifier",
    ),
    SensorEntityDescription(
        key="hardware_version",
        name="Hardware Version",
        icon="mdi:identifier",
    ),
    SensorEntityDescription(
        key="software_version",
        name="Software Version",
        icon="mdi:identifier",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: PionEvChargerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        PionEvChargerSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class PionEvChargerSensor(PionEvChargerEntity, SensorEntity):
    """pion_evcharger Sensor class."""

    def __init__(
        self,
        coordinator: PionEvChargerDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        return self.coordinator.data.get("body")
