#!/usr/bin/env python3
"""
Monitor Raspberry Pi Imager Module
Monitors the Raspberry Pi Imager process and detects when flashing is complete.
"""

import psutil
import time
import sys
from .detect_os import OSDetector


def find_imager_process():
    """Find the running Raspberry Pi Imager process."""
    process_names = [
        "rpi-imager.exe",
        "rpi-imager",
        "Raspberry Pi Imager",
        "imager.exe",
        "imager"
    ]

    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            proc_name = proc.info['name'].lower() if proc.info['name'] else ""
            proc_exe = proc.info['exe'].lower() if proc.info['exe'] else ""

            for name in process_names:
                if name.lower() in proc_name or name.lower() in proc_exe:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return None


def monitor_imager_process(process):
    """Monitor the Raspberry Pi Imager process until it closes."""
    print("\n" + "=" * 60)
    print("MONITORING RASPBERRY PI IMAGER")
    print("=" * 60)
    print(f"Process ID: {process.pid}")
    print(f"Process Name: {process.name()}")
    print("\nWaiting for Raspberry Pi Imager to close...")
    print("(The script will automatically exit when you close the Imager)\n")

    try:
        # Wait for the process to finish
        while process.is_running():
            time.sleep(2)  # Check every 2 seconds

        print("=" * 60)
        print("Raspberry Pi Imager has been closed")
        print("Flashing complete!")
        print("=" * 60)
        return True

    except KeyboardInterrupt:
        print("\n\nMonitoring interrupted by user")
        print("Raspberry Pi Imager is still running.")
        return False
    except Exception as e:
        print(f"\nError monitoring process: {e}")
        return False


def wait_for_imager_to_close():
    """Wait for the Raspberry Pi Imager to be opened and then monitor it until closed."""
    print("\n" + "=" * 60)
    print("WAITING FOR RASPBERRY PI IMAGER")
    print("=" * 60)
    print("Waiting for Raspberry Pi Imager to start...")

    max_wait_time = 30  # Wait up to 30 seconds for the process to start
    elapsed_time = 0
    check_interval = 1  # Check every second

    # Wait for the process to start
    while elapsed_time < max_wait_time:
        process = find_imager_process()
        if process:
            print(f"Raspberry Pi Imager detected (PID: {process.pid})")
            # Monitor the process until it closes
            return monitor_imager_process(process)

        time.sleep(check_interval)
        elapsed_time += check_interval
        if elapsed_time % 5 == 0:  # Print status every 5 seconds
            print(f"  Still waiting... ({elapsed_time}s / {max_wait_time}s)")

    print(f"\nRaspberry Pi Imager process not detected within {max_wait_time} seconds")
    print("The program may have already been running or failed to start.")
    return False


def monitor_and_wait():
    """Main function to monitor Raspberry Pi Imager."""
    # Check if the process is already running
    existing_process = find_imager_process()

    if existing_process:
        print("\nRaspberry Pi Imager is already running")
        return monitor_imager_process(existing_process)
    else:
        # Wait for the process to start and then monitor it
        return wait_for_imager_to_close()
