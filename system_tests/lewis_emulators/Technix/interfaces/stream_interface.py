from lewis.adapters.stream import StreamInterface, Cmd
from lewis.utils.command_builder import CmdBuilder
from lewis.core.logging import has_log
from lewis.utils.replies import conditional_reply


@has_log
class TechnixStreamInterface(StreamInterface):
    commands = {
        CmdBuilder("set_voltage").escape("d1,").int().eos().build(),
        CmdBuilder("get_voltage").escape("a1").eos().build(),
        CmdBuilder("set_current").escape("d2,").int().eos().build(),
        CmdBuilder("get_current").escape("a2").eos().build(),
        CmdBuilder("set_hv_on").escape("P5,").int().eos().build(),
        CmdBuilder("set_hv_off").escape("P6,").int().eos().build(),
        CmdBuilder("set_local_mode").escape("P7,").int().eos().build(),
        CmdBuilder("set_inhibit").escape("P8,").int().eos().build(),
        CmdBuilder("get_mains").escape("F").eos().build(),
        CmdBuilder("get_status").escape("E").eos().build(),

    }
    OutTerminator = "\r";
    InTerminator = "\r\n";
    def __init__(self):
        super(TechnixStreamInterface, self).__init__()
        # Commands that we expect via serial during normal operation
        self.commands = {
            CmdBuilder(self.catch_all).arg("^#9.*$").build()  # Catch-all command for debugging
        }

    def set_voltage(self, voltage_sp):
        self.device.voltage = voltage_sp
        print(f"Voltage: {voltage_sp}")

    def get_voltage(self):
        return f"Voltage: {self.device.voltage}"

    def set_current(self, current_sp):
        self.device.current = current_sp
        print(f"Current: {current_sp}")

    def get_current(self):
        return f"Current: {self.device.current}"

    def set_hv_on(self, hv_on_sp):
        self.device.hv_on = hv_on_sp
        print(f"HV is on: {hv_on_sp}")

    def set_hv_off(self, hv_off_sp):
        self.device.hv_off = hv_off_sp
        print(f"HV is off: {hv_off_sp}")

    def set_local_mode(self, local_mode_sp):
        self.device.local_mode = local_mode_sp
        print(f"Local mode is on: {local_mode_sp}")

    def set_inhibit(self, inhibit_sp):
        self.device.inhbit = inhibit_sp
        print(f"Is inhibit mode: {inhibit_sp}")

    def get_mains(self):
        return f"Mains information: {self.device.inhibit}"

    def get_status(self):
        return f"Image of the power supply logical status: {self.device.status}"

    def handle_error(self, request, error):
        """
        If command is not recognised print and error

        Args:
            request: requested string
            error: problem

        """
        self.log.error("An error occurred at request " + repr(request) + ": " + repr(error))

    def catch_all(self, command):
        pass
