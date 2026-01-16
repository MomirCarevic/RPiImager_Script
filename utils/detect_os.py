#!/usr/bin/env python3
"""
OS Detection Module
Detects the operating system and provides system-specific configurations.
"""

import platform
import sys
import os


class OSDetector:
    """Detects and provides information about the operating system."""

    def __init__(self):
        self.system = platform.system()
        self.release = platform.release()
        self.version = platform.version()
        self.machine = platform.machine()
        self.processor = platform.processor()

    def get_os_type(self):
        """Returns the operating system type."""
        return self.system

    def is_windows(self):
        """Check if running on Windows."""
        return self.system == "Windows"

    def is_linux(self):
        """Check if running on Linux."""
        return self.system == "Linux"

    def is_macos(self):
        """Check if running on macOS."""
        return self.system == "Darwin"

    def is_admin(self):
        """Check if script is running with administrator/root privileges."""
        try:
            if self.is_windows():
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception as e:
            print(f"Warning: Could not determine admin status: {e}")
            return False

    def get_disk_command(self):
        """Returns the appropriate command to list disks based on OS."""
        if self.is_windows():
            return "wmic diskdrive list brief"
        elif self.is_linux():
            return "lsblk -o NAME,SIZE,TYPE,MOUNTPOINT"
        elif self.is_macos():
            return "diskutil list"
        else:
            return None

    def get_detailed_info(self):
        """Returns detailed system information."""
        info = {
            "OS": self.system,
            "Release": self.release,
            "Version": self.version,
            "Machine": self.machine,
            "Processor": self.processor,
            "Python Version": sys.version,
            "Admin/Root": self.is_admin()
        }
        return info

    def print_system_info(self):
        """Prints formatted system information."""
        print("=" * 60)
        print("SYSTEM INFORMATION")
        print("=" * 60)

        info = self.get_detailed_info()
        for key, value in info.items():
            print(f"{key:20}: {value}")

        print("=" * 60)

        # Print OS-specific notes
        if self.is_windows():
            print("\n[Windows Detected]")
            print("  - Run as Administrator for SD card operations")
            print("  - Use 'diskpart' or 'wmic' to manage disks")
        elif self.is_linux():
            print("\n[Linux Detected]")
            print("  - Run with 'sudo' for SD card operations")
            print("  - Use 'lsblk' or 'fdisk' to manage disks")
        elif self.is_macos():
            print("\n[macOS Detected]")
            print("  - Run with 'sudo' for SD card operations")
            print("  - Use 'diskutil' to manage disks")

        # Admin/Root warning
        if not self.is_admin():
            print("\nWARNING: Not running with administrator/root privileges!")
            print("  SD card operations will require elevated permissions.")
        else:
            print("\nRunning with administrator/root privileges")

        print("=" * 60)


def detect_and_display():
    """Convenience function to detect OS and display information."""
    detector = OSDetector()
    detector.print_system_info()

    # Display the disk listing command for the current OS
    disk_cmd = detector.get_disk_command()
    if disk_cmd:
        print(f"\nTo list available disks, run: {disk_cmd}")

    return detector
