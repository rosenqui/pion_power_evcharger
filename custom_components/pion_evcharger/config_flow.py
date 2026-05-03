"""Adds config flow for PionEvCharger."""

from __future__ import annotations

import typing as t

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.loader import async_get_loaded_integration
from pion_power_api import (
    PionApiError,
    PionAuthError,
    PionConnectionError,
    PionPowerAPIClient,
)

from .const import CONF_PION_DEVICE_CODE, DEFAULT_URL, DOMAIN, LOGGER


class PionEvChargerFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for PionEvCharger."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, t.Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                client = PionPowerAPIClient(
                    base_url=DEFAULT_URL,
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    httpx_client=get_async_client(self.hass),
                )
                await client.login()
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
                # TODO(rosenqui): this is where we need to enumerate the devices and let the user select which one(s) to add. For now we just add the first one.

                for station in await client.get_station_list():
                    LOGGER.debug("Found station: %s", station)
                    for device in await station.get_devices():
                        LOGGER.debug("Found device: %s", device)
                        await self.async_set_unique_id(unique_id=f"{device.station_code}-{device.device_code}")
                        self._abort_if_unique_id_configured()
                        user_input[CONF_PION_DEVICE_CODE] = device.device_code
                        return self.async_create_entry(title=device.device_name, data=user_input)

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
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME, vol.UNDEFINED),
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
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, t.Any] | None = None) -> ConfigFlowResult:
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema({}),
            )
        return await self.async_step_user()
