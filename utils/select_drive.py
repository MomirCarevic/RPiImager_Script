#!/usr/bin/env python3
"""
Select Drive Module
Lists available drives and allows user to select one for flashing.
"""

import psutil
import platform
import subprocess
import os
from pathlib import Path
from .detect_os import OSDetector


class DriveInfo:
    """Class to store drive information."""

    def __init__(self, device, mountpoint, fstype, size, label=""):
        self.device = device
        self.mountpoint = mountpoint
        self.fstype = fstype
        self.size = size
        self.label = label

    def __str__(self):
        size_gb = self.size / (1024**3) if self.size else 0
        label_str = f" [{self.label}]" if self.label else ""
        mount_str = f" (mounted at {self.mountpoint})" if self.mountpoint else " (not mounted)"
        return f"{self.device}{label_str}: {size_gb:.2f} GB - {self.fstype}{mount_str}"


def get_windows_drives():
    """Get list of drives on Windows."""
    drives = []

    # Get all disk partitions
    partitions = psutil.disk_partitions(all=True)

    for partition in partitions:
        try:
            # Skip network drives and CD-ROM drives
            if 'cdrom' in partition.opts.lower() or partition.fstype == '':
                continue

            # Get usage information
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                size = usage.total
            except (PermissionError, OSError):
                size = 0

            # Get volume label using wmic
            label = ""
            try:
                result = subprocess.run(
                    f'wmic logicaldisk where "DeviceID=\'{partition.device.rstrip("\\")}\'" get VolumeName',
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        label = lines[1].strip()
            except:
                pass

            drive = DriveInfo(
                device=partition.device,
                mountpoint=partition.mountpoint,
                fstype=partition.fstype,
                size=size,
                label=label
            )
            drives.append(drive)

        except Exception as e:
            print(f"Warning: Could not get info for {partition.device}: {e}")

    # Also try to get physical disk information
    try:
        result = subprocess.run(
            'wmic diskdrive get DeviceID,Size,Caption,MediaType',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout:
            print("\nPhysical Disks Information:")
            print(result.stdout)
    except:
        pass

    return drives


def get_linux_drives():
    """Get list of drives on Linux."""
    drives = []

    # Get all disk partitions
    partitions = psutil.disk_partitions(all=False)

    for partition in partitions:
        try:
            # Get usage information
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                size = usage.total
            except (PermissionError, OSError):
                size = 0

            # Get label using lsblk
            label = ""
            try:
                device_name = partition.device.split('/')[-1]
                result = subprocess.run(
                    ['lsblk', '-no', 'LABEL', partition.device],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.stdout:
                    label = result.stdout.strip()
            except:
                pass

            drive = DriveInfo(
                device=partition.device,
                mountpoint=partition.mountpoint,
                fstype=partition.fstype,
                size=size,
                label=label
            )
            drives.append(drive)

        except Exception as e:
            print(f"Warning: Could not get info for {partition.device}: {e}")

    # Show lsblk output for additional information
    try:
        result = subprocess.run(
            ['lsblk', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE,LABEL,MODEL'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout:
            print("\nBlock Devices Information (lsblk):")
            print(result.stdout)
    except:
        pass

    return drives


def get_macos_drives():
    """Get list of drives on macOS."""
    drives = []

    # Get all disk partitions
    partitions = psutil.disk_partitions(all=False)

    for partition in partitions:
        try:
            # Get usage information
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                size = usage.total
            except (PermissionError, OSError):
                size = 0

            # Get label
            label = ""
            if partition.mountpoint and partition.mountpoint != '/':
                label = os.path.basename(partition.mountpoint)

            drive = DriveInfo(
                device=partition.device,
                mountpoint=partition.mountpoint,
                fstype=partition.fstype,
                size=size,
                label=label
            )
            drives.append(drive)

        except Exception as e:
            print(f"Warning: Could not get info for {partition.device}: {e}")

    # Show diskutil output for additional information
    try:
        result = subprocess.run(
            ['diskutil', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout:
            print("\nDisk Utility Information:")
            print(result.stdout)
    except:
        pass

    return drives


def list_available_drives():
    """List all available drives on the system."""
    detector = OSDetector()

    print("=" * 60)
    print("AVAILABLE DRIVES")
    print("=" * 60)

    if not detector.is_admin():
        print("\nWARNING: Not running with administrator/root privileges!")
        print("  You may not see all devices or be able to write to them.\n")

    drives = []

    if detector.is_windows():
        drives = get_windows_drives()
    elif detector.is_linux():
        drives = get_linux_drives()
    elif detector.is_macos():
        drives = get_macos_drives()
    else:
        print(f"Unsupported operating system: {detector.get_os_type()}")
        return []

    if not drives:
        print("No drives detected")
        return []

    print(f"\nFound {len(drives)} drive(s):\n")

    for i, drive in enumerate(drives, 1):
        print(f"[{i}] {drive}")

    print("\n" + "=" * 60)

    return drives


def select_drive():
    """Allow user to select a drive from the list."""
    drives = list_available_drives()

    if not drives:
        print("\nNo drives available to select")
        return None

    print("\nIMPORTANT: Make sure to select the correct drive!")
    print("WARNING: All data on the selected drive will be erased during flashing!\n")

    while True:
        try:
            choice = input("Enter the number of the drive you want to use (or 'q' to quit): ").strip()

            if choice.lower() == 'q':
                print("Selection cancelled.")
                return None

            drive_index = int(choice) - 1

            if 0 <= drive_index < len(drives):
                selected_drive = drives[drive_index]
                print(f"\nSelected: {selected_drive}")

                # Ask for confirmation
                confirm = input(f"\nAre you sure you want to use {selected_drive.device}? (yes/no): ").strip().lower()

                if confirm == 'yes':
                    print(f"Drive {selected_drive.device} confirmed")
                    return selected_drive
                else:
                    print("Selection cancelled. Please choose again.\n")
                    continue
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(drives)}")

        except ValueError:
            print("Invalid input. Please enter a number or 'q' to quit")
        except KeyboardInterrupt:
            print("\n\nSelection cancelled by user")
            return None


def get_drive_info(device_path):
    """Get detailed information about a specific drive."""
    detector = OSDetector()

    print("\n" + "=" * 60)
    print(f"DRIVE INFORMATION: {device_path}")
    print("=" * 60)

    try:
        # Get partition information
        partitions = [p for p in psutil.disk_partitions(all=True) if p.device == device_path]

        if partitions:
            partition = partitions[0]
            print(f"Device: {partition.device}")
            print(f"Mount Point: {partition.mountpoint}")
            print(f"File System: {partition.fstype}")

            try:
                usage = psutil.disk_usage(partition.mountpoint)
                print(f"Total Size: {usage.total / (1024**3):.2f} GB")
                print(f"Used: {usage.used / (1024**3):.2f} GB")
                print(f"Free: {usage.free / (1024**3):.2f} GB")
                print(f"Usage: {usage.percent}%")
            except:
                print("Could not get usage information")

        # OS-specific detailed info
        if detector.is_windows():
            try:
                device_id = device_path.rstrip('\\')
                result = subprocess.run(
                    f'wmic logicaldisk where "DeviceID=\'{device_id}\'" get *',
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                print("\nDetailed Information:")
                print(result.stdout)
            except:
                pass

        elif detector.is_linux():
            try:
                result = subprocess.run(
                    ['lsblk', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE,LABEL,MODEL,SERIAL', device_path],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                print("\nDetailed Information:")
                print(result.stdout)
            except:
                pass

        elif detector.is_macos():
            try:
                result = subprocess.run(
                    ['diskutil', 'info', device_path],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                print("\nDetailed Information:")
                print(result.stdout)
            except:
                pass

    except Exception as e:
        print(f"Error getting drive information: {e}")

    print("=" * 60)


if __name__ == "__main__":
    # Test the drive selection
    selected = select_drive()

    if selected:
        print(f"\n{'=' * 60}")
        print("SELECTION COMPLETE")
        print("=" * 60)
        print(f"You selected: {selected.device}")
        print(f"This drive will be used for flashing the Raspberry Pi image")
        print("=" * 60)

        # Show detailed information
        get_drive_info(selected.device)
