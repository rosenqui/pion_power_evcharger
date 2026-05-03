"""Custom types for pion_evcharger."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration
    from pion_power_api import Device, DeviceData, DeviceStats, PionPowerAPIClient

    from .coordinator import PionEvChargerDataUpdateCoordinator


type PionEvChargerConfigEntry = ConfigEntry[PionEvChargerData]


@dataclass
class PionEvChargerData:
    """Configuration data for the PionEvCharger integration."""

    client: PionPowerAPIClient
    coordinator: PionEvChargerDataUpdateCoordinator
    integration: Integration


@dataclass
class PionEvChargerDeviceData:
    """Data about a PionEvCharger device(s)."""

    device: Device
    """Device object representing the Pion Power device."""
    device_data: dict[str, DeviceData]
    """A dictionary mapping signal ids to DeviceData objects."""
    device_stats: DeviceStats
    """DeviceStats object representing the daily/monthly/yearly/total stats of the device."""

    def __eq__(self, other: object) -> bool:
        """Check equality based on device, device_data, and device_stats."""
        if not isinstance(other, PionEvChargerDeviceData):
            return False
        return self.device == other.device and self.device_data == other.device_data and self.device_stats == other.device_stats

    def __hash__(self) -> int:
        """Hash based on device, device_data, and device_stats."""
        return hash((self.device, tuple(sorted(self.device_data.items())), self.device_stats))
