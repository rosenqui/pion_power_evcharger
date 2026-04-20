"""Custom types for pion_evcharger."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import MockPionPowerAPIClient
    from .coordinator import PionEvChargerDataUpdateCoordinator


type PionEvChargerConfigEntry = ConfigEntry[PionEvChargerData]


@dataclass
class PionEvChargerData:
    """Data for the PionEvCharger integration."""

    client: MockPionPowerAPIClient
    coordinator: PionEvChargerDataUpdateCoordinator
    integration: Integration
