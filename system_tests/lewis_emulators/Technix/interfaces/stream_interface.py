from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply


@has_log
class TechnixStreamInterface(StreamInterface):
    commands = {
        CmdBuilder("set_voltage").escape("d1,").float().eos().build(),
        CmdBuilder("get_voltage").escape("a1").eos().build(),
        CmdBuilder("set_current").escape("d2,").float().eos().build(),
        CmdBuilder("get_current").escape("a2").eos().build(),
        CmdBuilder("set_hv_on").escape("P5,").int().eos().build(),
        CmdBuilder("set_hv_off").escape("P6,").int().eos().build(),
        CmdBuilder("set_local_mode").escape("P7,").int().eos().build(),
        CmdBuilder("set_inhibit").escape("P8,").int().eos().build(),
        CmdBuilder("get_mains").escape("F").eos().build(),
        CmdBuilder("get_status").escape("E").eos().build(),
    }

    in_terminator = "\r"
    out_terminator = "\r"

    @conditional_reply("connected")
    def set_voltage(self, voltage_sp):
        self.device.voltage = voltage_sp
        print(f"Voltage: {voltage_sp}")
        return f"d1,{int(voltage_sp)}"

    @conditional_reply("connected")
    def get_voltage(self):
        return f"a1{int(self.device.voltage)}"

    @conditional_reply("connected")
    def set_current(self, current_sp):
        self.device.current = current_sp
        print(f"Current: {int(current_sp)}")
        return f"d2,{int(current_sp)}"

    @conditional_reply("connected")
    def get_current(self):
        return f"a2{int(self.device.current)}"

    @conditional_reply("connected")
    def set_hv_on(self, hv_on_sp):
        if hv_on_sp == 0 and self.device.hv_on == 1:
            self.device.hv_status = 1
        self.device.hv_on = hv_on_sp
        print(f"HV is on: {hv_on_sp}")
        return f"P5,{hv_on_sp}"

    @conditional_reply("connected")
    def set_hv_off(self, hv_off_sp):
        if hv_off_sp == 0 and self.device.hv_off == 1:
            self.device.hv_status = 0
        self.device.hv_off = hv_off_sp
        print(f"HV is off: {hv_off_sp}")
        return f"P6,{hv_off_sp}"

    @conditional_reply("connected")
    def get_hv_status(self):
        return self.device.hv_status

    @conditional_reply("connected")
    def set_local_mode(self, local_mode_sp):
        self.device.local_mode = local_mode_sp
        print(f"Local mode is: {local_mode_sp}")

    @conditional_reply("connected")
    def set_inhibit(self, inhibit_sp):
        self.device.inhibit = inhibit_sp
        print(f"Inhibit mode: {inhibit_sp}")
        return f"P8,{inhibit_sp}"

    @conditional_reply("connected")
    def get_interlock(self):
        return self.device.interlock

    @conditional_reply("connected")
    def get_fault_status(self):
        return self.device.fault_status

    @conditional_reply("connected")
    def get_mains(self):
        return f"F{int(self.device.mains):03d}"

    @conditional_reply("connected")
    def get_status(self):
        status = (
            (self.device.fault_status * 2)
            + (self.device.interlock * 4)
            + (self.device.hv_status * 8)
            + (self.device.local_mode * 64)
            + (self.device.inhibit * 128)
        )
        return f"E{status}"

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
