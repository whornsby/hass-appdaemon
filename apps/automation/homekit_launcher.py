import appdaemon.plugins.hass.hassapi as hass


class HomekitLauncher(hass.Hass):

    def initialize(self):
        # load configs
        # register man loop callback
        pass

    def cb_check_device_status(self):
        # check if all homekit enabled devices are ready
        # if all_devices_registered
        #   start homekit (method call?)
        # else
        #   not register this method to run in 1 min
        pass
