"""Adds config flow for PionEvCharger."""

from __future__ import annotations

import typing as t

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers import selector
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.loader import async_get_loaded_integration
from pion_power_api import Device, PionApiError, PionAuthError, PionConnectionError, PionPowerAPIClient, Station

from .const import CONF_PION_DEVICE_CODE, CONF_PION_STATION_CODE, DEFAULT_URL, DOMAIN, LOGGER


class PionEvChargerFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for PionEvCharger."""

    VERSION = 1
    reauth_entry: ConfigEntry | None = None

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._client: PionPowerAPIClient | None = None
        self._devices: list[Device] | None = None
        self._selected_station_code: str | None = None
        self._selected_device_code: str | None = None
        self._stations: list[Station] | None = None
        self._user_email: str | None = None
        self._user_password: str | None = None

    async def async_step_user(
        self,
        user_input: dict[str, t.Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                self._client = PionPowerAPIClient(
                    base_url=DEFAULT_URL,
                    username=user_input[CONF_EMAIL],
                    password=user_input[CONF_PASSWORD],
                    httpx_client=get_async_client(self.hass),
                )
                await self._client.login()
            except PionAuthError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except PionConnectionError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except PionApiError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                self._user_email = user_input[CONF_EMAIL]
                self._user_password = user_input[CONF_PASSWORD]
                return await self.async_step_select_station()

        integration = async_get_loaded_integration(self.hass, DOMAIN)
        assert integration.documentation is not None, (  # noqa: S101
            "Integration documentation URL is not set in manifest.json"
        )

        return self.async_show_form(
            step_id="user",
            description_placeholders={
                "documentation_url": integration.documentation,
            },
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_EMAIL,
                        default=(user_input or {}).get(CONF_EMAIL, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.EMAIL,
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def async_step_reauth(self, entry_data: t.Mapping[str, t.Any]) -> ConfigFlowResult:  # noqa: ARG002
        """Perform reauth upon an API authentication error."""
        self.reauth_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, t.Any] | None = None) -> ConfigFlowResult:
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema({}),
            )
        return await self.async_step_user()

    async def async_step_select_station(self, user_input: dict[str, t.Any] | None = None) -> ConfigFlowResult:
        """Handle station selection."""
        if user_input is None:
            if self._client is None:
                return await self.async_step_user()
            self._stations = await self._client.get_station_list()
            if len(self._stations) == 1:
                self._selected_station_code = self._stations[0].station_code
                LOGGER.debug("Only one station found, selecting station: %s", self._selected_station_code)
                return await self.async_step_select_device()
            if len(self._stations) == 0:
                LOGGER.error("No stations found for the user")
                return self.async_abort(reason="no_stations")
            # More than 1 station - get the user to pick which one they want to use.
            return self.async_show_form(
                step_id="select_station",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_PION_STATION_CODE,
                            default=self._stations[0].station_code,
                        ): selector.SelectSelector(
                            selector.SelectSelectorConfig(
                                options=[
                                    {"label": station.station_name, "value": station.station_code} for station in self._stations
                                ],
                                sort=True,
                                mode=selector.SelectSelectorMode.LIST
                                if len(self._stations) <= 5  # noqa: PLR2004
                                else selector.SelectSelectorMode.DROPDOWN,
                            ),
                        )
                    },
                ),
            )
        self._selected_station_code = user_input[CONF_PION_STATION_CODE]
        LOGGER.debug("Selected station: %s", self._selected_station_code)
        return await self.async_step_select_device()

    async def async_step_select_device(self, user_input: dict[str, t.Any] | None = None) -> ConfigFlowResult:  # noqa: PLR0911
        """Handle device selection."""
        if user_input is None:
            if self._client is None:
                return await self.async_step_user()
            if self._selected_station_code is None:
                return await self.async_step_select_station()
            self._devices = await self._client.get_device_list(station_code=self._selected_station_code)
            if len(self._devices) == 0:
                LOGGER.error("No devices found for the selected station: %s", self._selected_station_code)
                return self.async_abort(reason="no_devices")
            if len(self._devices) == 1:
                self._selected_device_code = self._devices[0].device_code
                LOGGER.debug("Only one device found, selecting device: %s", self._selected_device_code)
            else:
                return self.async_show_form(
                    step_id="select_device",
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_PION_DEVICE_CODE, default=self._devices[0].device_code): selector.SelectSelector(
                                selector.SelectSelectorConfig(
                                    options=[
                                        {"label": device.device_name, "value": device.device_code} for device in self._devices
                                    ],
                                    sort=True,
                                    mode=selector.SelectSelectorMode.LIST
                                    if len(self._devices) <= 5  # noqa: PLR2004
                                    else selector.SelectSelectorMode.DROPDOWN,
                                ),
                            )
                        },
                    ),
                )
        # We end up here if the user selected a device from the form, or if there was only one device and we auto-selected it.
        # In either case we should have a selected device code, but we check just in case.
        if self._selected_device_code is None and user_input is not None:
            self._selected_device_code = user_input[CONF_PION_DEVICE_CODE]
        if self._selected_device_code is None:
            return self.async_abort(reason="no_devices")
        LOGGER.debug("Selected device: %s", self._selected_device_code)
        assert self._devices is not None, "Device list is not initialized"  # noqa: S101
        device_name = next(
            (device.device_name for device in self._devices if device.device_code == self._selected_device_code), None
        )
        assert device_name is not None, "Selected device code does not match any device"  # noqa: S101
        user_input = {
            CONF_EMAIL: self._user_email,
            CONF_PASSWORD: self._user_password,
            CONF_PION_STATION_CODE: self._selected_station_code,
            CONF_PION_DEVICE_CODE: self._selected_device_code,
        }
        if self.reauth_entry is not None:
            LOGGER.debug("Reauth flow - updating existing entry: %s", self.reauth_entry.entry_id)
            self.hass.config_entries.async_update_entry(self.reauth_entry, data=user_input)
            await self.hass.config_entries.async_reload(self.reauth_entry.entry_id)
            return self.async_abort(reason="reauth_successful")

        LOGGER.debug("New config flow - creating new entry")
        return self.async_create_entry(title=device_name, data=user_input)
