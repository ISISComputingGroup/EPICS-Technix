import contextlib
import unittest

from utils.channel_access import ChannelAccess
from utils.ioc_launcher import get_default_ioc_dir
from utils.test_modes import TestModes
from utils.testing import get_running_lewis_and_ioc, skip_if_recsim, parameterized_list
from parameterized import parameterized

DEVICE_PREFIX = "TECHNIX_01"

IOCS = [
    {
        "name": DEVICE_PREFIX,
        "directory": get_default_ioc_dir("TECHNIX"),
        "macros": {
            # 150kV, 4mA is realistic for real hardware
            "MAX_VOLT": "150",
            "MAX_CURR": "4",
            "LIMIT_ALARM": "MAJOR"
        },
        "emulator": "Technix",

    },
]


##############################################
#
#       Useful functions to run tests
#
##############################################

def _set_local_mode(ca, mode):
    ca.set_pv_value("LOCAL_MODE:SP", mode)


def _set_inhibit(ca, mode):
    ca.set_pv_value("INHIBIT:SP", mode)


TEST_MODES = [TestModes.DEVSIM]


class TechnixTests(unittest.TestCase):
    """
    Tests for the Technix IOC.
    """

    def setUp(self):
        self._lewis, self._ioc = get_running_lewis_and_ioc("Technix", DEVICE_PREFIX)
        self.ca = ChannelAccess(device_prefix=DEVICE_PREFIX, default_timeout=10)
        self.ca.set_pv_value("CURRENT.HIGH", self.ca.get_pv_value("CURRENT:SP.DRVH"))
        self.ca.set_pv_value("CURRENT.LOW", -1)
        self.ca.set_pv_value("VOLT.HIGH", self.ca.get_pv_value("VOLT:SP.DRVH"))
        self.ca.set_pv_value("VOLT.LOW", -1)

    @skip_if_recsim("Cannot catch errors in RECSIM")
    def test_WHEN_set_voltage_THEN_get_voltage_back_correctly(self):
        max_volt = self.ca.get_pv_value("VOLT:SP.DRVH")
        self.ca.set_pv_value("VOLT:SP", max_volt, wait=True)
        self.ca.assert_that_pv_is_number("VOLT", max_volt, tolerance=0.1)
        # as we have set max voltage, ADC should be full range
        self.ca.assert_that_pv_is("_VRAW.RVAL", 4095)
    
    @parameterized.expand([
        ("current_within_limits", 1, 0.5,  0, "CURRENT", "No"),
        ("current_outside_limits", 0.5, 1,  2,"CURRENT", "CURR LIMIT"),
        ("volt_within_limits", 1, 0.5,  0, "VOLT", "No"),
        ("volt_outside_limits", 0.5, 1,  1,"VOLT", "VOLT LIMIT"),
    ])
    @skip_if_recsim("Cannot catch errors in RECSIM")
    def test_WHEN_setpoint_set_AND_limits_set_THEN_limit_correct(self, _, limit, setpoint, summary_limit_status, current_volt, limit_enum):
        max = self.ca.get_pv_value(f"{current_volt}:SP.DRVH")
        self.ca.set_pv_value(f"{current_volt}.HIGH", max*limit)
        self.ca.set_pv_value(f"{current_volt}.LOW", 0)
        self.ca.set_pv_value(f"{current_volt}:SP", max*setpoint)
        self.ca.assert_that_pv_is_number(f"{current_volt}", max*setpoint, tolerance=0.1)
        self.ca.assert_that_pv_is("LIMIT", summary_limit_status)
        self.ca.assert_that_pv_is("LIMIT:ENUM", limit_enum)

    @skip_if_recsim("Cannot catch errors in RECSIM")
    def test_WHEN_both_outside_limits_THEN_both_limit(self):
        max_current = self.ca.get_pv_value("CURRENT:SP.DRVH")
        max_volt = self.ca.get_pv_value("VOLT:SP.DRVH")
        self.ca.set_pv_value("CURRENT.HIGH", max_current/2)
        self.ca.set_pv_value("CURRENT.LOW", 0)
        self.ca.set_pv_value("VOLT.HIGH", max_volt/2)
        self.ca.set_pv_value("VOLT.LOW", 0)
        self.ca.set_pv_value("CURRENT:SP", max_current)
        self.ca.set_pv_value("VOLT:SP", max_volt)
        self.ca.assert_that_pv_is("LIMIT", 3)
        self.ca.assert_that_pv_is("LIMIT:ENUM", "BOTH LIMITS")


    @skip_if_recsim("Cannot catch errors in RECSIM")
    def test_WHEN_set_current_THEN_get_current_back_correctly(self):
        max_curr = self.ca.get_pv_value("CURRENT:SP.DRVH")
        self.ca.set_pv_value("CURRENT:SP", max_curr, wait=True)
        self.ca.assert_that_pv_is_number("CURRENT", max_curr, tolerance=0.1)
        # as we have set max current, ADC should be full range
        self.ca.assert_that_pv_is("_CRAW.RVAL", 4095)

    @skip_if_recsim("Cannot catch errors in RECSIM")
    def test_WHEN_set_local_mode_THEN_mode_is_local(self):
        _set_local_mode(self.ca, "LOCAL")
        self.ca.assert_that_pv_is("LOCAL_MODE:SP", "LOCAL")

    @skip_if_recsim("Cannot catch errors in RECSIM")
    def test_WHEN_set_remote_mode_THEN_mode_is_remote(self):
        _set_local_mode(self.ca, "REMOTE")
        self.ca.assert_that_pv_is("LOCAL_MODE:SP", "REMOTE")

    @skip_if_recsim("Cannot catch errors in RECSIM")
    def test_WHEN_set_inhibit_to_idle_THEN_inhibit_is_idle(self):
        _set_inhibit(self.ca, "IDLE")
        self.ca.assert_that_pv_is("INHIBIT:SP", "IDLE")

    @skip_if_recsim("Cannot catch errors in RECSIM")
    def test_WHEN_set_inhibit_to_active_THEN_inhibit_is_active(self):
        _set_inhibit(self.ca, "ACTIVE")
        self.ca.assert_that_pv_is("INHIBIT:SP", "ACTIVE")

    @skip_if_recsim("Requires lewis backdoor")
    def test_WHEN_mains_status_set_THEN_status_can_be_read_back(self):
        self._lewis.backdoor_set_on_device("mains", 0)
        self.ca.assert_that_pv_is("ARC", "No arc present")

        self._lewis.backdoor_set_on_device("mains", 1)
        self.ca.assert_that_pv_is("ARC", "Arc present")

    @skip_if_recsim("Requires lewis backdoor")
    def test_WHEN_voltage_is_set_via_backdoor_THEN_correct(self):
        # Voltage in emulator is parts per 4095 but in DB is kV
        self._lewis.backdoor_set_on_device("voltage", int((123.456/150.)*4095))
        self.ca.assert_that_pv_is("_VRAW", int((123.456/150.)*4095))
        self.ca.assert_that_pv_is_number("VOLT", 123.456, tolerance=0.1)

    @skip_if_recsim("Required lewis backdoor")
    def test_WHEN_current_set_via_backdoor_THEN_correct(self):
        # Current is in parts per 4095 on device but mA in DB
        self._lewis.backdoor_set_on_device("current", int((1.23456/4.)*4095))
        self.ca.assert_that_pv_is("_CRAW", int((1.23456/4.)*4095))
        self.ca.assert_that_pv_is_number("CURRENT", 1.23456, tolerance=0.001)

    @parameterized.expand(parameterized_list([
        "VOLT", "CURRENT", "HV:STATUS", "LOCAL_MODE",
        "INTERLOCK", "FAULT", "INHIBIT", "ARC", "VOLT_CURR_REG"
    ]))
    @skip_if_recsim("Need emulator to test disconnected behaviour")
    def test_WHEN_device_disconnected_THEN_records_are_in_alarm(self, _, record):
        self.ca.assert_that_pv_alarm_is(record, self.ca.Alarms.NONE)
        with self._lewis.backdoor_simulate_disconnected_device():
            self.ca.assert_that_pv_alarm_is(record, self.ca.Alarms.INVALID)
        # Assert alarms clear on reconnection
        self.ca.assert_that_pv_alarm_is(record, self.ca.Alarms.NONE)
