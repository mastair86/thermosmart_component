"""
Support for Thermosmart sensor (boiler information).
For more details about this platform, please refer to the documentation at
??
"""

import logging

import voluptuous as vol

from custom_components import thermosmart
import homeassistant.helpers.config_validation as cv
from homeassistant.const import ATTR_ENTITY_ID, ATTR_NAME, CONF_NAME
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify

DEPENDENCIES = ['thermosmart']

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = thermosmart.SENSOR_LIST


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Thermosmart platform."""
    name = discovery_info['name']

    sensors = []
    _LOGGER.debug("Setting up platform")

    for _sensor in list(SENSOR_TYPES.keys()):
        new_sensor = ThermosmartSensor(name, hass.data[thermosmart.DOMAIN], _sensor)
        sensors.append(new_sensor)
    add_entities(sensors)

    return True


class ThermosmartSensor(Entity):
    """Representation of a Thermosmart sensor."""

    def __init__(self, name, data, sensor, should_fire_event=False):
        """Initialize the sensor."""
        self._data = data
        self._client = self._data.thermosmart
        if name:
            self._name = name
        else:
            self._name = self._client.id
        self._client_id = self._client.id
        self.should_fire_event = should_fire_event
        self.sensor = sensor
        self._unit_of_measurement = SENSOR_TYPES.get(sensor, '')
        self._state = None
        self.type = None
        self.update_without_throttle = False

    def __str__(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def name(self):
        """Get the name of the sensor."""
        return "{} {}".format(self._name, self.sensor)

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return self._unit_of_measurement

    def update(self):
        """Get the latest state of the sensor."""
        if self.update_without_throttle:
            self._data.update(no_throttle=True)
            self.update_without_throttle = False
        else:
            self._data.update()
           
        if self._client.latest_update.get('ot'):
            self._state = self._client.latest_update['ot']['readable'][self.sensor]
        else:
            self._state = None