import os
import json
import logging
from models.device_model import DeviceModel

def analyze_dump(dump_folder):
    analyzer = DumpAnalyzer(dump_folder)
    result = analyzer.analyze()
    return result['device_model']['model'] if result['device_model'] else "Unknown", result['touchwiz_version']

class DumpAnalyzer:
    def __init__(self, dump_folder):
        self.dump_folder = dump_folder

    def analyze(self):
        try:
            device_model = self._detect_device_model()
            touchwiz_version = self._detect_touchwiz_version()
            kernel_version = self._detect_kernel_version()

            analysis_result = {
                "device_model": device_model.to_dict() if device_model else None,
                "touchwiz_version": touchwiz_version,
                "kernel_version": kernel_version
            }

            logging.info(f"Dump analysis completed: {json.dumps(analysis_result, indent=2)}")
            return analysis_result
        except Exception as e:
            logging.error(f"Error during dump analysis: {str(e)}")
            raise

    def _detect_device_model(self):
        build_prop_path = os.path.join(self.dump_folder, "system", "build.prop")
        if os.path.exists(build_prop_path):
            with open(build_prop_path, 'r') as f:
                content = f.read()
                model = self._extract_property(content, "ro.product.model")
                manufacturer = self._extract_property(content, "ro.product.manufacturer")
                return DeviceModel(model, manufacturer)
        return None

    def _detect_touchwiz_version(self):
        # This is a placeholder. In a real implementation, you'd need to analyze
        # specific files or properties to determine the TouchWiz/OneUI version
        return "Unknown"

    def _detect_kernel_version(self):
        kernel_path = os.path.join(self.dump_folder, "boot", "kernel")
        if os.path.exists(kernel_path):
            # In a real implementation, you'd need to analyze the kernel file
            # to extract its version. This might involve running strings on the file
            # and looking for version information.
            return "Found (version detection not implemented)"
        return "Not found"

    def _extract_property(self, content, property_name):
        for line in content.splitlines():
            if line.startswith(property_name):
                return line.split('=')[1].strip()
        return None

