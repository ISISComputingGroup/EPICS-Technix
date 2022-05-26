from collections import OrderedDict
from .states import DefaultState
from lewis.devices import StateMachineDevice


class SimulatedTechnix(StateMachineDevice):

    def _initialize_data(self):
        """
        Initialize all of the device's attributes.
        """
        self.connected = True
        self.speed = 1
        self.voltage = 0.0
        self.current = 0.0
        self.hv_on = 0
        self.hv_off = 0
        self.local_mode = 0
        self.inhibit = 0
        self.inhibit_status = 0
        self.mains = 0
        self.status = 0
        self.interlock = 0
        self.fault_status = 0
        self.hv_status = 0


        # When the device is in an error state it can respond with junk
        self.is_giving_errors = False
        self.out_error = "}{<7f>w"
        self.out_terminator_in_error = ""

    def _get_state_handlers(self):
        return {
            'default': DefaultState(),
        }

    def _get_initial_state(self):
        return 'default'

    def _get_transition_handlers(self):
        return OrderedDict([
        ])

