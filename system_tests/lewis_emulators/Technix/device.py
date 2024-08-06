from collections import OrderedDict

from lewis.devices import StateMachineDevice

from .states import DefaultState


class SimulatedTechnix(StateMachineDevice):
    def _initialize_data(self):
        """
        Initialize all of the device's attributes.
        """
        self.connected = True
        self.voltage = 0.0
        self.current = 0.0
        self.hv_on = 0
        self.hv_off = 0
        self.local_mode = 0
        self.inhibit = 0
        self.mains = 0
        self.status = 0
        self.interlock = 0
        self.fault_status = 0
        self.hv_status = 0

    def _get_state_handlers(self):
        return {
            "default": DefaultState(),
        }

    def _get_initial_state(self):
        return "default"

    def _get_transition_handlers(self):
        return OrderedDict([])
