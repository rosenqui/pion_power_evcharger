"""Switch platform for pion_evcharger."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .entity import PionEvChargerEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import PionEvChargerDataUpdateCoordinator
    from .data import PionEvChargerConfigEntry, PionEvChargerDeviceData

ENTITY_DESCRIPTIONS = (
    SwitchEntityDescription(
        key="pion_evcharger",
        name="Integration Switch",
        icon="mdi:format-quote-close",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: PionEvChargerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    async_add_entities(
        PionEvChargerSwitch(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class PionEvChargerSwitch(PionEvChargerEntity, SwitchEntity):
    """pion_evcharger switch class."""

    def __init__(self, coordinator: PionEvChargerDataUpdateCoordinator, entity_description: SwitchEntityDescription) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator, entity_description.key)
        self.entity_description = entity_description

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        device_data = cast("PionEvChargerDeviceData", self.coordinator.data)
        signal = device_data.device_data.get("90100006", None)
        if signal:
            return float(signal.signal_value) == 4.0  # noqa: PLR2004
        return False

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the switch."""
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the switch."""
        await self.coordinator.async_request_refresh()
