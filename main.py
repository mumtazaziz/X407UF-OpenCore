import os
import shutil
from tempfile import mkdtemp
from zipfile import ZipFile
import helper


preserved_acpi_files = [
    'SSDT-EC-USBX.aml',
    'SSDT-PLUG.aml',
    'SSDT-PNLF.aml'
]

preserved_driver_files = [
    'AudioDxe.efi',
    'CrScreenshotDxe.efi',
    'OpenCanopy.efi',
    'OpenRuntime.efi',
    'ResetNvramEntry.efi',
    'ToggleSipEntry.efi'
]

preserved_tool_files = [
    'OpenShell.efi'
]


def getOpenCore(outdir: str, tempdir: str = mkdtemp(), cachedir: str | None = None):
    downloaded_path = helper.downloadLatestReleaseFromGitHub(
        'acidanthera/OpenCorePkg', cachedir)
    with ZipFile(downloaded_path) as downloaded_zip:
        print('Extracting...')
        downloaded_zip.extractall(tempdir)
        # Move EFI folder
        shutil.move(os.path.join(tempdir, 'X64', 'EFI'), outdir)
        # Move SSDTs
        for acpi_file in preserved_acpi_files:
            shutil.move(
                os.path.join(tempdir, 'Docs', 'AcpiSamples',
                             'Binaries', acpi_file),
                os.path.join(outdir, 'EFI', 'OC', 'ACPI',
                             acpi_file))
        # Remove unnecessary drivers
        temp_drivers_dir = os.path.join(outdir, 'EFI', 'OC', '_Drivers')
        dest_drivers_dir = os.path.join(outdir, 'EFI', 'OC', 'Drivers')
        os.rename(dest_drivers_dir, temp_drivers_dir)
        os.mkdir(dest_drivers_dir)
        for driver_file in preserved_driver_files:
            shutil.move(
                os.path.join(temp_drivers_dir, driver_file),
                os.path.join(dest_drivers_dir, driver_file))
        shutil.rmtree(temp_drivers_dir)
        # Remove unnecessary tools
        temp_tools_dir = os.path.join(outdir, 'EFI', 'OC', '_Tools')
        dest_tools_dir = os.path.join(outdir, 'EFI', 'OC', 'Tools')
        os.rename(dest_tools_dir, temp_tools_dir)
        os.mkdir(dest_tools_dir)
        for tool_file in preserved_tool_files:
            shutil.move(
                os.path.join(temp_tools_dir, tool_file),
                os.path.join(dest_tools_dir, tool_file))
        shutil.rmtree(temp_tools_dir)

        shutil.copyfile('config.plist', outdir+'/EFI/OC/config.plist')
        print('OpenCore extracted to ' + outdir)
        shutil.rmtree(tempdir)


def getKext(repo: str, outdir: str, kextfiles: list[str] | None = None, tempdir: str = mkdtemp(), cachedir: str | None = None):
    if kextfiles is None:
        kextfiles = [repo.split('/')[1] + '.kext']
    downloaded_path = helper.downloadLatestReleaseFromGitHub(repo, cachedir)
    with ZipFile(downloaded_path) as downloaded_zip:
        print('Extracting...')
        downloaded_zip.extractall(tempdir)
        # Move kext
        if os.path.exists(os.path.join(tempdir, 'Kexts')):
            kextfiles = list(os.path.join('Kexts', x) for x in kextfiles)
        for kextfile in kextfiles:
            shutil.move(
                os.path.join(tempdir, kextfile),
                os.path.join(outdir, 'EFI', 'OC', 'Kexts'))
        print('Kext extracted to ' + outdir)
        shutil.rmtree(tempdir)


def main(outdir: str = 'dist', cachedir: str = 'downloads'):
    helper.prepareOutput(outdir)
    helper.prepareCache(cachedir)
    # Gathering files
    getOpenCore(outdir, cachedir=cachedir)
    getKext('acidanthera/AppleALC', outdir, cachedir=cachedir)
    getKext('acidanthera/BrcmPatchRAM', outdir, kextfiles=[
        'BlueToolFixup.kext'
    ], cachedir=cachedir)
    getKext('acidanthera/CpuTscSync', outdir, cachedir=cachedir)
    getKext('acidanthera/Lilu', outdir, cachedir=cachedir)
    getKext('acidanthera/VoodooPS2', outdir, kextfiles=[
        'VoodooPS2Controller.kext'
    ], cachedir=cachedir)
    getKext('acidanthera/VirtualSMC', outdir, kextfiles=[
        'VirtualSMC.kext',
        'SMCBatteryManager.kext',
        'SMCProcessor.kext',
        'SMCSuperIO.kext',
    ], cachedir=cachedir)
    getKext('acidanthera/WhateverGreen', outdir, cachedir=cachedir)
    getKext('hieplpvip/AsusSMC', outdir, cachedir=cachedir)
    getKext('OpenIntelWireless/IntelBluetoothFirmware', outdir, kextfiles=[
        'IntelBluetoothFirmware.kext',
        'IntelBluetoothInjector.kext',
        'IntelBTPatcher.kext',
    ], cachedir=cachedir)
    getKext('VoodooI2C/VoodooI2C', outdir, kextfiles=[
        'VoodooI2C.kext',
        'VoodooI2CHID.kext'
    ], cachedir=cachedir)
    helper.cleanupCache(cachedir)


if __name__ == "__main__":
    main()
