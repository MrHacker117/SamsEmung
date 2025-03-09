import json
import os

DEFAULT_CONFIG = {
    "qemu_path": "",
    "qemu_executable": "",
    "samsung_models": {
        "Galaxy S10": "arm64",
        "Galaxy S20": "arm64",
        "Galaxy Note 10": "arm64",
        "SM-G900F": "arm"
    },
    "dump_folder": "",
    "boot_img_path": "",
    "virtual_disk_size": 4096,
    "virtual_disk_path": "",
    "touchwiz_versions": ["TouchWiz 5", "TouchWiz 6", "TouchWiz 7"],
    "oneui_versions": ["One UI 1.0", "One UI 2.0", "One UI 3.0"],
    "font": "default"
}

CONFIG_FILE = "samsemung_config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            loaded_config = json.load(f)

        config = DEFAULT_CONFIG.copy()
        config.update(loaded_config)
    else:
        config = DEFAULT_CONFIG.copy()

    return config


def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


CONFIG = load_config()

