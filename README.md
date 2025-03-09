### SamsEmung - Samsung Device Emulator

A powerful emulator for Samsung devices that supports both full-system emulation (QEMU) and CPU-level emulation (Unicorn Engine).





## Overview

SamsEmung is an advanced emulation platform designed specifically for Samsung devices. It provides a flexible architecture that can switch between full-system emulation using QEMU and CPU-level emulation using Unicorn Engine, depending on your needs and available resources.

## Key Features

- **Dual Emulation Paths**: Automatically selects between QEMU (full-system) and Unicorn Engine (CPU-level)
- **Samsung-Specific Components**: Emulates Exynos SoCs, TouchWiz/One UI, Knox security features
- **Device Support**: Covers multiple Samsung Galaxy models (S6 through S10, Note series)
- **Firmware Analysis**: Extract and analyze boot.img, system dumps, and DTB files
- **VirtualBox-Style UI**: Intuitive interface for managing virtual devices
- **Peripheral Emulation**: Supports touchscreen, buttons, sensors, and other device-specific hardware


## Architecture

SamsEmung implements two distinct emulation paths:

### QEMU Path (Full-System Emulation)

```plaintext
┌──────────────────────────────┐ ┌──────────────────────────────┐
│ Host Machine                 │ │ Emulated Samsung Device      │
├──────────────────────────────┤ ├──────────────────────────────┤
│ 1. Подготовка образов:       │ │                              │
│    - boot.img                │ │                              │
│    - system.dump             │ │                              │
│    - vendor.img              │ │───mount─────►                │
│ 2. Конфигурация QEMU:        │ │ 3. Инициализация виртуального│
│    - Выбор машины: virt      │ │    железа:                   │
│    - CPU: cortex-a78         │ │    - Загрузчик (U-Boot)      │
│    - Память: 8G              │ │    - Инициализация ядра      │
│    - Устройства:             │ │    - Монтирование разделов   │
│      * virtio-gpu            │ │                              │
│      * virtio-blk            │ │                              │
│                              │◄──IRQ/MMIO──┤                  │
│ 4. Запуск эмуляции:          │ │ 5. Загрузка Android:         │
│    qemu-system-aarch64 ...   │ │    - Init Process            │
│                              │◄─ADB/USB────┤    - Запуск Zygote│
│ 6. Взаимодействие:           │ │    - Запуск TouchWiz         │
│    - ADB подключение         │ │                              │
│    - Графический интерфейс   │ │                              │
└──────────────────────────────┘ └──────────────────────────────┘
```

### Unicorn Engine Path (CPU-Level Emulation)

```plaintext
┌──────────────────────────────┐ ┌──────────────────────────────┐
│ Host Application             │ │ Emulated CPU (ARM64)         │
├──────────────────────────────┤ ├──────────────────────────────┤
│ 1. Инициализация Unicorn:    │ │                              │
│    - Архитектура: ARM64      │ │                              │
│    - Режим: ARM              │ │                              │
│                              │───mem_map───►                  │
│ 2. Настройка памяти:         │ │ 3. Загрузка кода:            │
│    - Код: 0x80000000         │ │    - Чтение бинарника        │
│    - Стек: 0x90000000        │ │    (например, из boot.img)   │
│    - Данные: 0xA0000000      │ │                              │
│                              │◄──hook──────┤                  │
│ 4. Регистрация хуков:        │ │ 5. Выполнение инструкций:    │
│    - Трассировка кода        │ │    - Пошагово или блоками    │
│    - Перехват SVC/SMC        │ │                              │
│                              │◄──callback──┤                  │
│ 6. Обработка исключений:     │ │ 7. Эмуляция периферии:       │
│    - Ручная эмуляция         │ │    - Системные вызовы        │
│    MMIO/регистров            │ │    - Память/таймеры          │
└──────────────────────────────┘ └──────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- PyQt6
- QEMU 6.0+ (for full-system emulation)
- Unicorn Engine 2.0+ (for CPU-level emulation)


### Setup

1. Clone the repository:

```shellscript
git clone https://github.com/MrHacker117/SamsEmung.git
cd SamsEmung
```


2. Install dependencies:

```shellscript
pip install -r requirements.txt
```


3. Install QEMU (optional, for full-system emulation):

1. **Linux**: `sudo apt install qemu-system-arm`
2. **macOS**: `brew install qemu`
3. **Windows**: Download from [QEMU website](https://www.qemu.org/download/)





## Usage

### Starting the Emulator

```shellscript
python main.py
```

### Creating a New Virtual Device

1. Click "New" in the toolbar
2. Select a device model (e.g., Galaxy S10)
3. Configure settings (memory, storage, etc.)
4. Click "OK" to create the device


### Running a Virtual Device

1. Select a device from the list
2. Click "Start" in the toolbar
3. The emulator will launch using the appropriate emulation path


### Analyzing Firmware

```python
from dump_analyzer import analyze_dump

# Analyze a Samsung firmware dump
ui_version, device_model = analyze_dump("/path/to/dump")
print(f"Detected device: {device_model} running {ui_version}")
```

## Configuration

The emulator can be configured through the UI or by editing the `config.json` file:

```json
{
  "qemu_path": "/usr/bin",
  "dump_folder": "/path/to/dumps",
  "virtual_memory": 2048,
  "samsung_models": {
    "SM-G900F": {
      "name": "Galaxy S5",
      "arch": "arm64",
      "cpu": "cortex-a57",
      "memory": 2048,
      "display": {
        "width": 1080,
        "height": 1920,
        "density": 480
      }
    }
  }
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- QEMU project for the full-system emulation capabilities
- Unicorn Engine for the CPU emulation framework
- Samsung for creating the devices we're emulating


## Disclaimer

This project is not affiliated with, authorized by, endorsed by, or in any way officially connected with Samsung Electronics Co., Ltd., or any of its subsidiaries or affiliates. The official Samsung website can be found at [www.samsung.com](https://www.samsung.com).
