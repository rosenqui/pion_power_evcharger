"""Sensor platform for pion_evcharger."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from homeassistant.components.sensor import DOMAIN, SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.const import (
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTemperature,
)

from .data import PionEvChargerDeviceData
from .entity import PionEvChargerEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from pion_power_api import Device, DeviceData, DeviceStats

    from .coordinator import PionEvChargerDataUpdateCoordinator
    from .data import PionEvChargerConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="90100009",
        name="Reason for stopping charging",
        icon="mdi:octagon",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="90100200",
        name="Leakage current",
        icon="mdi:current-ac",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="90100204",
        name="Max current",
        icon="mdi:current-ac",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="90100206",
        name="Current",
        icon="mdi:current-ac",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="90100210",
        name="Plug temperature",
        icon="mdi:thermometer",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="90100211",
        name="Male Connector temperature",
        icon="mdi:thermometer",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="90100300",
        name="Voltage",
        icon="mdi:sine-wave",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: PionEvChargerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    device_data = PionEvChargerDeviceData(
        device=cast("Device", entry.runtime_data.coordinator.data.get("device")),
        device_data=cast("dict[str, DeviceData]", entry.runtime_data.coordinator.data.get("device_data")),
        device_stats=cast("DeviceStats", entry.runtime_data.coordinator.data.get("device_stats")),
    )
    async_add_entities(
        PionEvChargerSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
            device_data=device_data,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class PionEvChargerSensor(PionEvChargerEntity, SensorEntity):
    """pion_evcharger Sensor class."""

    def __init__(
        self,
        coordinator: PionEvChargerDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
        device_data: PionEvChargerDeviceData,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._key = entity_description.key
        self._device_data = device_data
        self._attr_unique_id = f"{DOMAIN}_{self._device_data.device.device_code}_{self._key}"

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        signal = self._device_data.device_data.get(self._key)
        if signal:
            if self._key == "90100009" and signal.signal_meaning:
                return signal.signal_meaning
            return signal.signal_value
        return None
