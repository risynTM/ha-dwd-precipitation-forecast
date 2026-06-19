"""Config flow for DWD Precipitation Forecast integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE

from .const import DOMAIN
from .dwdradar import DWDRadar

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate that the chosen location can be used.

    The DWD radar product only covers Germany and the immediately surrounding
    region, so reject locations outside the radar grid. This check is pure
    geometry and needs no network access.
    """
    if not DWDRadar().is_in_area(data[CONF_LATITUDE], data[CONF_LONGITUDE]):
        raise NotInArea

    return {"title": data["name"]}


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DWD Precipitation Forecast."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except NotInArea:
                errors["base"] = "not_in_area"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name", default=self.hass.config.location_name): str,
                vol.Required(CONF_LATITUDE, default=self.hass.config.latitude): float,
                vol.Required(CONF_LONGITUDE, default=self.hass.config.longitude): float,
            }),
            errors=errors
        )


class NotInArea(HomeAssistantError):
    """Error to indicate the location is outside the DWD radar coverage area."""
