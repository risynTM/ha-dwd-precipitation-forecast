from datetime import timedelta
import logging

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .dwdradar import DWDRadar

_LOGGER = logging.getLogger(__name__)

type DwdPrecipitationForecastConfigEntry = ConfigEntry[
    DwdPrecipitationForecastCoordinator
]


class DwdPrecipitationForecastCoordinator(DataUpdateCoordinator):
    config_entry: DwdPrecipitationForecastConfigEntry
    api: DWDRadar

    def __init__(self, hass):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    async def async_config_entry_first_refresh(self) -> None:
        """Perform first refresh."""
        self.api = DWDRadar()

        await super().async_config_entry_first_refresh()

    async def _async_update_data(self):
        """Fetch the latest radar data from the DWD open-data API."""
        try:
            async with async_timeout.timeout(60):
                return await self.hass.async_add_executor_job(self.api.get_radars)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with DWD API: {err}") from err
