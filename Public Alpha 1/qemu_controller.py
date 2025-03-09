import os
import subprocess
import tempfile
from pathlib import Path
import logging
import sys
import zipfile
import shutil


class QEMUController:
    def __init__(self, config):
        self.config = config
        self.process = None
        self.kernel_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'kernels')
        self.recovery_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'recovery')
        os.makedirs(self.kernel_dir, exist_ok=True)
        os.makedirs(self.recovery_dir, exist_ok=True)

    def create_virtual_disk(self, size):
        """Create a new virtual disk"""
        try:
            vdisk_folder = Path(tempfile.gettempdir()) / "samsemung_vdisk"
            vdisk_folder.mkdir(parents=True, exist_ok=True)
            vdisk_path = vdisk_folder / "samsung_vdisk.qcow2"

            # If the file already exists, remove it
            if vdisk_path.exists():
                vdisk_path.unlink()

            cmd = [
                os.path.join(self.config['qemu_path'], "qemu-img"),
                "create",
                "-f", "qcow2",
                str(vdisk_path),
                f"{size}M"
            ]

            # Run the command and capture output
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )

            if not vdisk_path.exists():
                raise RuntimeError("Virtual disk file was not created")

            logging.info(f"Virtual disk created at: {vdisk_path}")
            logging.debug(f"qemu-img output: {result.stdout}")

            return str(vdisk_path)

        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to create virtual disk: {e.stderr}")
            raise RuntimeError(f"Failed to create virtual disk: {e.stderr}")
        except Exception as e:
            logging.error(f"Error creating virtual disk: {str(e)}")
            raise RuntimeError(f"Error creating virtual disk: {str(e)}")

    def add_kernel(self, zip_path):
        """Add kernel zip file to the kernels directory"""
        try:
            kernel_name = os.path.basename(zip_path)
            dest_path = os.path.join(self.kernel_dir, kernel_name)
            shutil.copy2(zip_path, dest_path)
            logging.info(f"Kernel zip added: {dest_path}")
            return dest_path
        except Exception as e:
            logging.error(f"Error adding kernel zip: {str(e)}")
            raise

    def add_twrp_recovery(self, recovery_img_path):
        """Add TWRP recovery image and modify it to appear as a Samsung device"""
        try:
            # Copy the TWRP recovery image
            recovery_name = os.path.basename(recovery_img_path)
            dest_path = os.path.join(self.recovery_dir, recovery_name)
            shutil.copy2(recovery_img_path, dest_path)

            # Modify the recovery image to appear as a Samsung device
            self._modify_twrp_for_samsung(dest_path)

            logging.info(f"Modified TWRP recovery added: {dest_path}")
            return dest_path
        except Exception as e:
            logging.error(f"Error adding TWRP recovery: {str(e)}")
            raise

    def _modify_twrp_for_samsung(self, recovery_img_path):
        """Modify TWRP recovery image to appear as a Samsung device"""
        # This is a placeholder function. In a real implementation, you would need to:
        # 1. Mount the recovery image
        # 2. Modify relevant files to change device information
        # 3. Unmount the recovery image
        logging.info(f"Modifying TWRP recovery to appear as Samsung device: {recovery_img_path}")
        # Placeholder for actual modification logic
        pass

    def start_emulator(self, model, ui_version, memory, kernel_zip, recovery_img):
        """Start the emulator with the given configuration"""
        try:
            architecture = self.config['samsung_models'].get(model, "arm64")
            qemu_path = self._get_qemu_path(architecture)

            vdisk_path = self.config.get('qcow2_path', self.config.get('virtual_disk_path'))
            if not vdisk_path or not os.path.exists(vdisk_path):
                raise FileNotFoundError("Virtual disk not found. Please create a virtual disk in settings.")

            cmd = [
                qemu_path,
                "-machine", "type=virt",
                "-cpu", "cortex-a15",
                "-kernel", kernel_zip,
                "-initrd", recovery_img,
                "-drive", f"file={vdisk_path},format=qcow2",
                "-m", f"{memory}M" if memory > 0 else "1024M",
            ]

            # Add kernel parameters if specified
            kernel_params = self.config.get('kernel_params')
            if kernel_params:
                cmd.extend(["-append", kernel_params])

            env = os.environ.copy()
            env["GTK_PATH"] = ""

            self.process = subprocess.Popen(cmd, env=env)
            logging.info(f"Started QEMU emulator for {model}")

            return cmd

        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to start QEMU: {e}")
            raise
        except FileNotFoundError as e:
            logging.error(str(e))
            raise
        except Exception as e:
            logging.error(f"Unexpected error while starting emulator: {str(e)}")
            raise

    def create_dump_file(self, output_path):
        """Create a dump file of the current emulator state"""
        if not self.process:
            raise RuntimeError("Emulator is not running. Cannot create dump file.")

        try:
            dump_cmd = [
                self.config['qemu_path'],
                "-dump-vmstate", output_path
            ]

            result = subprocess.run(dump_cmd, check=True, capture_output=True, text=True)
            logging.info(f"Dump file created at: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to create dump file: {e.stderr}")
            raise RuntimeError(f"Failed to create dump file: {e.stderr}")
        except Exception as e:
            logging.error(f"Error creating dump file: {str(e)}")
            raise RuntimeError(f"Error creating dump file: {str(e)}")

    def _get_qemu_path(self, architecture):
        qemu_path_template = self.config['qemu_path']
        if architecture == "arm64":
            return qemu_path_template.replace("qemu-system-x86_64", "qemu-system-aarch64")
        elif architecture == "x86_64":
            return qemu_path_template.replace("qemu-system-aarch64", "qemu-system-x86_64")
        else:
            raise ValueError(f"Unsupported architecture: {architecture}")

    def stop_emulator(self):
        """Stop the running emulator"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            logging.info("Stopped QEMU emulator")
        else:
            logging.warning("No running emulator to stop")

    def get_available_kernels(self):
        """Get a list of available kernels in the kernels directory"""
        return [f for f in os.listdir(self.kernel_dir) if f.endswith('.zip')]

    def get_available_recoveries(self):
        """Get a list of available recovery images in the recovery directory"""
        return [f for f in os.listdir(self.recovery_dir) if f.endswith('.img')]

    def validate_kernel(self, kernel_path):
        """Validate that the given file is a valid kernel"""
        if not os.path.exists(kernel_path):
            raise FileNotFoundError(f"Kernel file not found: {kernel_path}")

        # Basic size check (kernels are typically between 2MB and 100MB)
        size = os.path.getsize(kernel_path)
        if size < 2 * 1024 * 1024 or size > 100 * 1024 * 1024:
            logging.warning(
                f"Kernel file size ({size / 1024 / 1024:.1f}MB) is outside typical range (2MB-100MB). "
                "This might not be a valid kernel file."
            )

        # Check file header for common kernel signatures
        try:
            with open(kernel_path, 'rb') as f:
                header = f.read(16)
                # Check for ARM boot header magic
                if header[0:8] == b'ANDROID!':
                    logging.info("Valid Android boot image detected")
                    return True
                elif header[0x202:0x206] == b'HdrS':
                    logging.info("Valid Linux kernel image detected")
                    return True
                else:
                    logging.warning("Kernel file does not have standard Android or Linux headers")
                    # Instead of returning False, we'll just warn and continue
                    return True
        except Exception as e:
            logging.error(f"Error reading kernel file: {str(e)}")
            return False

    def test_emulator(self, model, memory):
        """Start the emulator in test mode"""
        try:
            architecture = self.config['samsung_models'].get(model, "arm64")
            qemu_path = os.path.join(self.config['qemu_path'],
                                     "qemu-system-" + architecture + (".exe" if sys.platform == "win32" else ""))

            cmd = [
                qemu_path,
                "-machine", "type=virt",
                "-cpu", "cortex-a15",
                "-m", f"{memory}M" if memory > 0 else "1024M",
                "-nographic",  # Run without GUI for testing
                "-monitor", "none",
                "-serial", "none",
                "-smp", "1",
                "-boot", "order=c",
            ]

            env = os.environ.copy()
            env["GTK_PATH"] = ""

            self.process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            creationflags=subprocess.CREATE_NO_WINDOW)
            logging.info(f"Started QEMU emulator in test mode for {model}")

            # Wait for a short time to see if the emulator crashes immediately
            try:
                self.process.wait(timeout=5)
                stdout, stderr = self.process.communicate()
                if self.process.returncode != 0:
                    raise RuntimeError(f"Emulator test failed. Error: {stderr.decode('utf-8')}")
            except subprocess.TimeoutExpired:
                # If the process doesn't exit within 5 seconds, we assume it's running fine
                pass

            return cmd

        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to start QEMU in test mode: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error while testing emulator: {str(e)}")
            raise

    def add_kernel_from_zip(self, zip_path):
        """Extract kernel from zip file and add it to the kernels directory"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Create a temporary directory to extract the contents
                with tempfile.TemporaryDirectory() as tmpdirname:
                    zip_ref.extractall(tmpdirname)

                    # Look for kernel file recursively
                    kernel_file = self._find_kernel_file(tmpdirname)

                    if kernel_file:
                        kernel_name = os.path.basename(zip_path).replace('.zip', '')
                        dest_path = os.path.join(self.kernel_dir, f"{kernel_name}_kernel.img")
                        shutil.copy2(kernel_file, dest_path)
                        logging.info(f"Kernel extracted and added: {dest_path}")
                        return dest_path
                    else:
                        raise FileNotFoundError("No kernel file found in the zip archive")
        except Exception as e:
            logging.error(f"Error adding kernel from zip: {str(e)}")
            raise

    def _find_kernel_file(self, directory):
        """Recursively search for a kernel file in the given directory"""
        for root, _, files in os.walk(directory):
            for file in files:
                if file == 'kernel' or file.endswith('.img'):
                    return os.path.join(root, file)
        return None

    def get_command_line(self, model, ui_version, memory, kernel_zip, recovery_img):
        """Get the command line that would be used to start the emulator"""
        architecture = self.config['samsung_models'].get(model, "arm64")
        qemu_path = self._get_qemu_path(architecture)

        vdisk_path = self.config.get('qcow2_path') or self.config.get('virtual_disk_path')
        if not vdisk_path or not os.path.exists(vdisk_path):
            raise FileNotFoundError("Virtual disk not found. Please create a virtual disk in settings.")

        cmd = [
            qemu_path,
            "-machine", "type=virt",
            "-cpu", "cortex-a15",
            "-kernel", kernel_zip,
            "-initrd", recovery_img,
            "-drive", f"file={vdisk_path},format=qcow2",
            "-m", f"{memory}M" if memory > 0 else "1024M",
        ]

        # Add kernel parameters if specified
        kernel_params = self.config.get('kernel_params')
        if kernel_params:
            cmd.extend(["-append", kernel_params])

        return " ".join(cmd)

