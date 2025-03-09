import unittest
from unittest.mock import patch, mock_open
from dump_analyzer import DumpAnalyzer
from models.device_model import DeviceModel

class TestDumpAnalyzer(unittest.TestCase):
    def setUp(self):
        self.dump_folder = '/path/to/dump'
        self.analyzer = DumpAnalyzer(self.dump_folder)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="ro.product.model=Galaxy S10\nro.product.manufacturer=Samsung")
    def test_detect_device_model(self, mock_file, mock_exists):
        mock_exists.return_value = True
        device_model = self.analyzer._detect_device_model()
        self.assertIsInstance(device_model, DeviceModel)
        self.assertEqual(device_model.model, 'Galaxy S10')
        self.assertEqual(device_model.manufacturer, 'Samsung')

    def test_detect_touchwiz_version(self):
        version = self.analyzer._detect_touchwiz_version()
        self.assertEqual(version, 'Unknown')

    @patch('os.path.exists')
    def test_detect_kernel_version(self, mock_exists):
        mock_exists.return_value = True
        version = self.analyzer._detect_kernel_version()
        self.assertEqual(version, 'Found (version detection not implemented)')

    @patch.object(DumpAnalyzer, '_detect_device_model')
    @patch.object(DumpAnalyzer, '_detect_touchwiz_version')
    @patch.object(DumpAnalyzer, '_detect_kernel_version')
    def test_analyze(self, mock_kernel, mock_touchwiz, mock_device):
        mock_device.return_value = DeviceModel('Galaxy S10', 'Samsung')
        mock_touchwiz.return_value = 'TouchWiz 9.0'
        mock_kernel.return_value = '4.14.78'

        result = self.analyzer.analyze()

        self.assertIsInstance(result, dict)
        self.assertEqual(result['device_model']['model'], 'Galaxy S10')
        self.assertEqual(result['touchwiz_version'], 'TouchWiz 9.0')
        self.assertEqual(result['kernel_version'], '4.14.78')

if __name__ == '__main__':
    unittest.main()

