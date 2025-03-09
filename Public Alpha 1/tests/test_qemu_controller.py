import unittest
from unittest.mock import patch, MagicMock
from qemu_controller import QEMUController

class TestQEMUController(unittest.TestCase):
    def setUp(self):
        self.config = {
            'qemu_path': '/path/to/qemu',
            'qemu_executable': 'qemu-system-arm',
            'samsung_models': {'Galaxy S10': 'arm64'},
            'dump_folder': '/path/to/dump'
        }
        self.controller = QEMUController(self.config)

    @patch('subprocess.Popen')
    def test_start_emulator(self, mock_popen):
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        self.controller.start_emulator('Galaxy S10', 'TouchWiz', 2048)

        mock_popen.assert_called_once()
        self.assertIsNotNone(self.controller.process)

    @patch('psutil.pid_exists')
    def test_is_running(self, mock_pid_exists):
        mock_pid_exists.return_value = True
        self.controller.process = MagicMock()
        self.controller.process.pid = 12345

        self.assertTrue(self.controller.is_running())

    @patch('subprocess.Popen')
    def test_stop_emulator(self, mock_popen):
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        self.controller.process = mock_process

        self.controller.stop_emulator()

        mock_process.terminate.assert_called_once()
        self.assertIsNone(self.controller.process)

    @patch('os.path.exists')
    def test_get_kernel_path(self, mock_exists):
        mock_exists.return_value = True
        kernel_path = self.controller._get_kernel_path('Galaxy S10')
        self.assertEqual(kernel_path, '/path/to/dump/boot/kernel')

if __name__ == '__main__':
    unittest.main()

