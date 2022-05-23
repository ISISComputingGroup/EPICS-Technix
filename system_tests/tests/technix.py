import unittest

from utils.channel_access import ChannelAccess
from utils.ioc_launcher import get_default_ioc_dir
from utils.test_modes import TestModes
from utils.testing import get_running_lewis_and_ioc, skip_if_recsim

DEVICE_PREFIX = "TECHNIX_01"

IOCS = [
    {
        "name": DEVICE_PREFIX,
        "directory": get_default_ioc_dir("TECHNIX"),
        "macros": {},
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


TEST_MODES = [TestModes.RECSIM, TestModes.DEVSIM]


class TechnixTests(unittest.TestCase):
    """
    Tests for the Technix IOC.
    """

    def setUp(self):
        self._lewis, self._ioc = get_running_lewis_and_ioc("Technix", DEVICE_PREFIX)
        self.ca = ChannelAccess(device_prefix=DEVICE_PREFIX)

    @skip_if_recsim("Cannot catch errors in RECSIM")
    def test_WHEN_set_voltage_THEN_get_voltage_back_correctly(self):
        max_volt = self.ca.get_pv_value("VOLT:SP.DRVH")
        self.ca.set_pv_value("VOLT:SP", max_volt, wait=True)
        self.ca.assert_that_pv_is("VOLT", max_volt)
        # as we have set max voltage, ADC should be full range
        self.ca.assert_that_pv_is("_VRAW.RVAL", 4095)

    @skip_if_recsim("Cannot catch errors in RECSIM")
    def test_WHEN_set_current_THEN_get_current_back_correctly(self):
        max_curr = self.ca.get_pv_value("CURRENT:SP.DRVH")
        self.ca.set_pv_value("CURRENT:SP", max_curr, wait=True)
        self.ca.assert_that_pv_is("CURRENT", max_curr)
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
