# SPDX-FileCopyrightText: 2022-2025 Espressif Systems (Shanghai) CO LTD
# SPDX-License-Identifier: Apache-2.0
# pylint: disable=W0621  # redefined-outer-name
import os
import time

import espefuse
import esptool
import pytest
import serial
from _pytest.fixtures import FixtureRequest
from _pytest.monkeypatch import MonkeyPatch
from pytest_embedded_idf.dut import IdfDut
from pytest_embedded_idf.serial import IdfSerial
from pytest_embedded_serial_esp.serial import EspSerial

efuse_reset_port = os.getenv('EFUSEPORT')
esp_port = os.getenv('ESPPORT')


# This is a custom Serial Class for the FPGA
class FpgaSerial(IdfSerial):
    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)

        self.efuse_reset_port = efuse_reset_port
        if self.efuse_reset_port is None:
            raise RuntimeError('EFUSEPORT not specified')

        self.esp_port = esp_port
        if self.esp_port is None:
            raise RuntimeError('ESPPORT not specified')

    @EspSerial.use_esptool()
    def bootloader_flash(self, bootloader_path: str) -> None:
        """
        Flash bootloader.

        :return: None
        """
        offs = int(self.app.sdkconfig.get('BOOTLOADER_OFFSET_IN_FLASH', 0))
        esptool.main(
            f'--port {self.esp_port} --no-stub write_flash {str(offs)} {bootloader_path} --force'.split(), esp=self.esp
        )

    @EspSerial.use_esptool()
    def partition_table_flash(self, partition_table_path: str) -> None:
        """
        Flash Partition Table.

        :return: None
        """
        offs = int(self.app.flash_args['partition-table']['offset'], 16)
        esptool.main(
            f'--port {self.esp_port} --no-stub write_flash {str(offs)} {partition_table_path}'.split(), esp=self.esp
        )

    @EspSerial.use_esptool()
    def app_flash(self, app_path: str) -> None:
        """
        Flash App.

        :return: None
        """
        offs = int(self.app.flash_args['app']['offset'], 16)
        esptool.main(f'--port {self.esp_port} --no-stub write_flash {str(offs)} {app_path}'.split(), esp=self.esp)

    def erase_app_header(self) -> None:
        """
        Erase app header

        :return None
        """
        if not os.path.exists('erase_app_header.bin'):
            binstr = b'\xff' * 4096
            with open('erase_app_header.bin', 'wb') as f:
                f.write(binstr)

        self.app_flash('erase_app_header.bin')

    @EspSerial.use_esptool()
    def burn_efuse_key_digest(self, key: str, purpose: str, block: str) -> None:
        espefuse.main(
            f'--port {self.esp_port} burn_key_digest {block} {key} {purpose} --do-not-confirm'.split(), esp=self.esp
        )

    @EspSerial.use_esptool()
    def burn_efuse(self, field: str, val: int) -> None:
        espefuse.main(f'--port {self.esp_port} burn_efuse {field} {str(val)} --do-not-confirm'.split(), esp=self.esp)

    @EspSerial.use_esptool()
    def burn_efuse_key(self, key: str, purpose: str, block: str) -> None:
        espefuse.main(f'--port {self.esp_port} burn_key {block} {key} {purpose} --do-not-confirm'.split(), esp=self.esp)

    def reset_efuses(self) -> None:
        with serial.Serial(self.efuse_reset_port) as efuseport:
            print('Resetting efuses')
            efuseport.dtr = 0
            self.proc.setRTS(0)
            time.sleep(1)
            efuseport.dtr = 1
            self.proc.setRTS(1)
            time.sleep(1)
            self.proc.setRTS(0)
            efuseport.dtr = 0


class FpgaDut(IdfDut):
    SECURE_BOOT_EN_KEY = None  # type: str
    SECURE_BOOT_EN_VAL = 0

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self.efuse_reset_port = efuse_reset_port


class Esp32c3FpgaDut(FpgaDut):
    SECURE_BOOT_EN_KEY = 'SECURE_BOOT_EN'
    SECURE_BOOT_EN_VAL = 1
    WAFER_VERSION = 'WAFER_VERSION_MINOR_LO'
    WAFER_VERSION_VAL = 3

    def burn_wafer_version(self) -> None:
        self.serial.burn_efuse(self.WAFER_VERSION, self.WAFER_VERSION_VAL)

    def secure_boot_burn_en_bit(self) -> None:
        self.serial.burn_efuse(self.SECURE_BOOT_EN_KEY, self.SECURE_BOOT_EN_VAL)

    def secure_boot_burn_digest(self, digest: str, key_index: int = 0, block: int = 0) -> None:
        self.serial.burn_efuse_key_digest(digest, 'SECURE_BOOT_DIGEST%d' % key_index, 'BLOCK_KEY%d' % block)


class Esp32s3FpgaDut(FpgaDut):
    SECURE_BOOT_EN_KEY = 'SECURE_BOOT_EN'
    SECURE_BOOT_EN_VAL = 1
    WAFER_VERSION = 'WAFER_VERSION_MINOR_LO'
    WAFER_VERSION_VAL = 1

    def burn_wafer_version(self) -> None:
        self.serial.burn_efuse(self.WAFER_VERSION, self.WAFER_VERSION_VAL)

    def secure_boot_burn_en_bit(self) -> None:
        self.serial.burn_efuse(self.SECURE_BOOT_EN_KEY, self.SECURE_BOOT_EN_VAL)

    def secure_boot_burn_digest(self, digest: str, key_index: int = 0, block: int = 0) -> None:
        self.serial.burn_efuse_key_digest(digest, 'SECURE_BOOT_DIGEST%d' % key_index, 'BLOCK_KEY%d' % block)


class Esp32p4FpgaDut(FpgaDut):
    SECURE_BOOT_EN_KEY = 'SECURE_BOOT_EN'
    SECURE_BOOT_EN_VAL = 1

    def burn_wafer_version(self) -> None:
        pass

    def secure_boot_burn_en_bit(self) -> None:
        self.serial.burn_efuse(self.SECURE_BOOT_EN_KEY, self.SECURE_BOOT_EN_VAL)

    def secure_boot_burn_digest(self, digest: str, key_index: int = 0, block: int = 0) -> None:
        self.serial.burn_efuse_key_digest(digest, 'SECURE_BOOT_DIGEST%d' % key_index, 'BLOCK_KEY%d' % block)


class Esp32c5FpgaDut(FpgaDut):
    SECURE_BOOT_EN_KEY = 'SECURE_BOOT_EN'
    SECURE_BOOT_EN_VAL = 1

    def burn_wafer_version(self) -> None:
        pass

    def secure_boot_burn_en_bit(self) -> None:
        self.serial.burn_efuse(self.SECURE_BOOT_EN_KEY, self.SECURE_BOOT_EN_VAL)

    def secure_boot_burn_digest(self, digest: str, key_index: int = 0, block: int = 0) -> None:
        self.serial.burn_efuse_key_digest(digest, 'SECURE_BOOT_DIGEST%d' % key_index, 'BLOCK_KEY%d' % block)


class Esp32c61FpgaDut(FpgaDut):
    SECURE_BOOT_EN_KEY = 'SECURE_BOOT_EN'
    SECURE_BOOT_EN_VAL = 1

    def burn_wafer_version(self) -> None:
        pass

    def secure_boot_burn_en_bit(self) -> None:
        self.serial.burn_efuse(self.SECURE_BOOT_EN_KEY, self.SECURE_BOOT_EN_VAL)

    def secure_boot_burn_digest(self, digest: str, key_index: int = 0, block: int = 0) -> None:
        self.serial.burn_efuse_key_digest(digest, 'SECURE_BOOT_DIGEST%d' % key_index, 'BLOCK_KEY%d' % block)


class Esp32h21FpgaDut(FpgaDut):
    SECURE_BOOT_EN_KEY = 'SECURE_BOOT_EN'
    SECURE_BOOT_EN_VAL = 1

    def burn_wafer_version(self) -> None:
        pass

    def secure_boot_burn_en_bit(self) -> None:
        self.serial.burn_efuse(self.SECURE_BOOT_EN_KEY, self.SECURE_BOOT_EN_VAL)

    def secure_boot_burn_digest(self, digest: str, key_index: int = 0, block: int = 0) -> None:
        self.serial.burn_efuse_key_digest(digest, 'SECURE_BOOT_DIGEST%d' % key_index, 'BLOCK_KEY%d' % block)


@pytest.fixture(scope='module')
def monkeypatch_module(request: FixtureRequest) -> MonkeyPatch:
    mp = MonkeyPatch()
    request.addfinalizer(mp.undo)
    return mp


@pytest.fixture(scope='module', autouse=True)
def replace_dut_class(monkeypatch_module: MonkeyPatch, pytestconfig: pytest.Config) -> None:
    FPGA_DUT_MAP = {
        'esp32c3': Esp32c3FpgaDut,
        'esp32s3': Esp32s3FpgaDut,
        'esp32p4': Esp32p4FpgaDut,
        'esp32c5': Esp32c5FpgaDut,
        'esp32c61': Esp32c61FpgaDut,
        'esp32h21': Esp32h21FpgaDut,
    }

    target = pytestconfig.getoption('target')
    fpga_dut_class = FPGA_DUT_MAP.get(target)
    if fpga_dut_class is None:
        raise ValueError(f'Unsupported target: {target}')

    monkeypatch_module.setattr('pytest_embedded_idf.IdfDut', fpga_dut_class)
    monkeypatch_module.setattr('pytest_embedded_idf.IdfSerial', FpgaSerial)
