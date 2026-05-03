"""Sensor platform for pion_evcharger."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import (
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)

from .entity import PionEvChargerEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import StateType
    from pion_power_api import DevicePeriodStats, DeviceStatValue

    from .coordinator import PionEvChargerDataUpdateCoordinator
    from .data import PionEvChargerConfigEntry, PionEvChargerDeviceData

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
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="90100204",
        name="Max current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="90100206",
        name="Current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="90100210",
        name="Plug temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="90100211",
        name="Male Connector temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="90100300",
        name="Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="90100306",
        name="Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        suggested_display_precision=1,
    ),
)

STATISTIC_ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="day_stat.ev_charge",
        name="Daily charging energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="day_stat.ev_charge_hours",
        name="Daily charging duration",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.HOURS,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="day_stat.ev_order_number",
        name="Daily charging sessions",
        icon="mdi:counter",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="month_stat.ev_charge",
        name="Monthly charging energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="month_stat.ev_charge_hours",
        name="Monthly charging duration",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.HOURS,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="month_stat.ev_order_number",
        name="Monthly charging sessions",
        icon="mdi:counter",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="year_stat.ev_charge",
        name="Yearly charging energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="year_stat.ev_charge_hours",
        name="Yearly charging duration",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.HOURS,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="year_stat.ev_order_number",
        name="Yearly charging sessions",
        icon="mdi:counter",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="total_stat.ev_charge",
        name="Total charging energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="total_stat.ev_charge_hours",
        name="Total charging duration",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.HOURS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="total_stat.ev_order_number",
        name="Total charging sessions",
        icon="mdi:counter",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: PionEvChargerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        PionEvChargerSensor(coordinator=entry.runtime_data.coordinator, entity_description=entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )
    async_add_entities(
        PionEvChargerSensorStatistic(coordinator=entry.runtime_data.coordinator, entity_description=entity_description)
        for entity_description in STATISTIC_ENTITY_DESCRIPTIONS
    )


class PionEvChargerSensor(PionEvChargerEntity, SensorEntity):
    """pion_evcharger Sensor class."""

    def __init__(self, coordinator: PionEvChargerDataUpdateCoordinator, entity_description: SensorEntityDescription) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, entity_description.key)

        self.entity_description = entity_description
        self._attr_has_entity_name = True
        self._attr_suggested_display_precision = entity_description.suggested_display_precision

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        device_data = cast("PionEvChargerDeviceData", self.coordinator.data)
        signal = device_data.device_data.get(self._key)
        if signal:
            if self._key == "90100009" and signal.signal_meaning:
                return signal.signal_meaning
            return signal.signal_value
        return None


class PionEvChargerSensorStatistic(PionEvChargerEntity, SensorEntity):
    """pion_evcharger Sensor statistic class."""

    def __init__(self, coordinator: PionEvChargerDataUpdateCoordinator, entity_description: SensorEntityDescription) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, entity_description.key)

        self._attr_has_entity_name = True
        self._attr_entity_registry_enabled_default = entity_description.entity_registry_enabled_default
        self._attr_suggested_display_precision = entity_description.suggested_display_precision
        self.entity_description = entity_description

        period, stat_key = entity_description.key.split(".")
        self._period = period
        self._stat_key = stat_key

    @property
    def native_value(self) -> StateType | None:
        """Return the native value of the sensor."""
        device_data = cast("PionEvChargerDeviceData", self.coordinator.data)
        period_stats = cast("DevicePeriodStats", getattr(device_data.device_stats, f"{self._period}", None))
        if period_stats:
            if self._stat_key == "ev_order_number":
                return int(getattr(period_stats, self._stat_key, 0))
            stat_value = cast("DeviceStatValue", getattr(period_stats, self._stat_key, None))
            if stat_value:
                return stat_value.value
        return None
