import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from adb import find_adb, list_devices, get_available_device, dial, hangup, is_call_active


class TestFindAdb(unittest.TestCase):
    @patch("shutil.which", return_value="C:\\adb\\adb.exe")
    def test_found_in_path(self, mock_which):
        self.assertEqual(find_adb(), "C:\\adb\\adb.exe")

    @patch("shutil.which", return_value=None)
    @patch("pathlib.Path.exists", return_value=False)
    def test_not_found(self, mock_exists, mock_which):
        with self.assertRaises(FileNotFoundError):
            find_adb()


class TestListDevices(unittest.TestCase):
    @patch("subprocess.run")
    def test_one_device(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="List of devices attached\nABC123\tdevice\n",
            stderr="",
        )
        devices = list_devices("adb")
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0]["serial"], "ABC123")
        self.assertEqual(devices[0]["status"], "device")

    @patch("subprocess.run")
    def test_no_devices(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="List of devices attached\n",
            stderr="",
        )
        devices = list_devices("adb")
        self.assertEqual(len(devices), 0)

    @patch("subprocess.run")
    def test_unauthorized(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="List of devices attached\nABC123\tunauthorized\n",
            stderr="",
        )
        devices = list_devices("adb")
        self.assertEqual(devices[0]["status"], "unauthorized")


class TestGetAvailableDevice(unittest.TestCase):
    @patch("adb.list_devices")
    def test_one_available(self, mock_list):
        mock_list.return_value = [{"serial": "ABC123", "status": "device"}]
        self.assertEqual(get_available_device("adb"), "ABC123")

    @patch("adb.list_devices")
    def test_none_available(self, mock_list):
        mock_list.return_value = []
        with self.assertRaises(ConnectionError):
            get_available_device("adb")

    @patch("adb.list_devices")
    def test_unauthorized(self, mock_list):
        mock_list.return_value = [{"serial": "ABC123", "status": "unauthorized"}]
        with self.assertRaises(PermissionError):
            get_available_device("adb")

    @patch("adb.list_devices")
    def test_offline(self, mock_list):
        mock_list.return_value = [{"serial": "ABC123", "status": "offline"}]
        with self.assertRaises(ConnectionError):
            get_available_device("adb")

    @patch("adb.list_devices")
    def test_multiple_takes_first(self, mock_list):
        mock_list.return_value = [
            {"serial": "AAA", "status": "device"},
            {"serial": "BBB", "status": "device"},
        ]
        self.assertEqual(get_available_device("adb"), "AAA")


class TestDial(unittest.TestCase):
    @patch("subprocess.run")
    def test_dial_command(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        result = dial("adb", "+5511999999999")
        mock_run.assert_called_once_with(
            [
                "adb",
                "shell",
                "am",
                "start",
                "-a",
                "android.intent.action.CALL",
                "-d",
                "tel:+5511999999999",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0)


class TestHangup(unittest.TestCase):
    @patch("subprocess.run")
    def test_hangup_command(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        result = hangup("adb")
        mock_run.assert_called_once_with(
            ["adb", "shell", "input", "keyevent", "KEYCODE_ENDCALL"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0)


class TestIsCallActive(unittest.TestCase):
    @patch("subprocess.run")
    def test_call_active(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="mCallState=2", stderr=""
        )
        self.assertTrue(is_call_active("adb"))

    @patch("subprocess.run")
    def test_call_idle(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="mCallState=0", stderr=""
        )
        self.assertFalse(is_call_active("adb"))

    @patch("subprocess.run", side_effect=Exception("error"))
    def test_error_returns_false(self, mock_run):
        self.assertFalse(is_call_active("adb"))


if __name__ == "__main__":
    unittest.main()
