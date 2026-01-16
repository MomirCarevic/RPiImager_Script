#!/usr/bin/env python3
"""
Open Raspberry Pi Imager Module
Opens the installed Raspberry Pi Imager application.
"""

import os
import subprocess
import re
from pathlib import Path
from .detect_os import OSDetector


def search_windows_program(program_name):
    """Search for installed programs on Windows."""
    found_paths = []

    # Method 1: Search registry for install location
    try:
        registry_paths = [
            r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
            r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        ]

        for reg_path in registry_paths:
            try:
                cmd = f'reg query "{reg_path}" /s /f "{program_name}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)

                if result.stdout:
                    display_name = None
                    install_location = None
                    current_key = None

                    for line in result.stdout.split('\n'):
                        if line.startswith('HKEY_'):
                            # Save previous entry if valid
                            if display_name and program_name.lower() in display_name.lower() and install_location:
                                found_paths.append(install_location)
                            # Reset for new key
                            display_name = None
                            install_location = None
                            current_key = line.strip()
                        elif 'DisplayName' in line and 'REG_SZ' in line:
                            match = re.search(r'DisplayName\s+REG_SZ\s+(.+)', line)
                            if match:
                                display_name = match.group(1).strip()
                        elif 'InstallLocation' in line and 'REG_SZ' in line:
                            match = re.search(r'InstallLocation\s+REG_SZ\s+(.+)', line)
                            if match:
                                install_location = match.group(1).strip()

                    # Check last entry
                    if display_name and program_name.lower() in display_name.lower() and install_location:
                        found_paths.append(install_location)
            except:
                pass
    except Exception as e:
        print(f"Registry search error: {e}")

    # Method 2: Check common Program Files locations
    program_files = [
        os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
        os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')
    ]

    # Check multiple possible installation paths
    possible_paths = [
        "Raspberry Pi Imager",
        "Raspberry Pi Ltd\\Imager",
        "RaspberryPiImager"
    ]

    for pf in program_files:
        for possible_path in possible_paths:
            potential_path = Path(pf) / possible_path
            if potential_path.exists():
                found_paths.append(str(potential_path))

    return found_paths


def find_imager_executable(install_location):
    """Find the actual executable in the install location."""
    install_path = Path(install_location)

    # Common executable names
    executable_names = [
        "rpi-imager.exe",
        "imager.exe",
        "Raspberry Pi Imager.exe"
    ]

    # Search in install location
    for exe_name in executable_names:
        exe_path = install_path / exe_name
        if exe_path.exists():
            return exe_path

    # Search in subdirectories
    try:
        for exe_name in executable_names:
            for file_path in install_path.rglob(exe_name):
                if file_path.is_file():
                    return file_path
    except:
        pass

    return None


def search_linux_program(program_name):
    """Search for installed programs on Linux."""
    found_paths = []

    # Method 1: which command
    try:
        result = subprocess.run(
            ['which', program_name],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and result.stdout.strip():
            found_paths.append(result.stdout.strip())
    except:
        pass

    # Method 2: whereis command
    try:
        result = subprocess.run(
            ['whereis', program_name],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.stdout.strip():
            output = result.stdout.strip()
            if ':' in output:
                paths = output.split(':', 1)[1].strip().split()
                found_paths.extend([p for p in paths if os.path.isfile(p)])
    except:
        pass

    # Method 3: Common installation paths
    common_paths = [
        '/usr/bin/rpi-imager',
        '/usr/local/bin/rpi-imager',
        '/opt/rpi-imager/rpi-imager'
    ]

    for path in common_paths:
        if os.path.isfile(path):
            found_paths.append(path)

    return found_paths


def search_macos_program(program_name):
    """Search for installed programs on macOS."""
    found_paths = []

    # Method 1: Check Applications folders
    app_locations = [
        Path("/Applications") / f"{program_name}.app",
        Path.home() / "Applications" / f"{program_name}.app",
        Path("/Applications") / "Raspberry Pi Imager.app",
        Path.home() / "Applications" / "Raspberry Pi Imager.app"
    ]

    for app_path in app_locations:
        if app_path.exists():
            found_paths.append(str(app_path))

    # Method 2: which command
    try:
        result = subprocess.run(
            ['which', program_name.lower().replace(' ', '-')],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and result.stdout.strip():
            found_paths.append(result.stdout.strip())
    except:
        pass

    return found_paths


def is_imager_installed():
    """Check if Raspberry Pi Imager is installed on the system."""
    detector = OSDetector()

    if detector.is_windows():
        found_paths = search_windows_program("Raspberry Pi Imager")
        if found_paths:
            exe_path = find_imager_executable(found_paths[0])
            return exe_path is not None
        return False

    elif detector.is_linux():
        found_paths = search_linux_program("rpi-imager")
        return len(found_paths) > 0

    elif detector.is_macos():
        found_paths = search_macos_program("Raspberry Pi Imager")
        return len(found_paths) > 0

    return False


def open_imager():
    """Open the installed Raspberry Pi Imager application."""
    detector = OSDetector()

    print("=" * 60)
    print("OPENING RASPBERRY PI IMAGER")
    print("=" * 60)

    found_paths = []

    # Search for installed program
    if detector.is_windows():
        print("Searching for installed Raspberry Pi Imager on Windows...")
        found_paths = search_windows_program("Raspberry Pi Imager")

        if found_paths:
            print(f"Found installation at: {found_paths[0]}")

            # Find the executable
            exe_path = find_imager_executable(found_paths[0])

            if exe_path:
                print(f"Found executable: {exe_path}")
                print("Opening Raspberry Pi Imager...")
                try:
                    subprocess.Popen([str(exe_path)], shell=True)
                    print("Raspberry Pi Imager opened successfully")
                    return True
                except Exception as e:
                    print(f"Error opening imager: {e}")
                    return False
            else:
                print(f"Could not find executable in {found_paths[0]}")
        else:
            print("Raspberry Pi Imager not found in registry")
            print("\nTrying alternative: checking Downloads folder...")

            # Fallback: Check Downloads folder for the downloaded file
            downloads = os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads')
            imager_path = Path(downloads) / "rpi-imager-latest.exe"

            if imager_path.exists():
                print(f"Found downloaded installer at: {imager_path}")
                print("Opening installer...")
                try:
                    subprocess.Popen([str(imager_path)], shell=True)
                    print("Installer opened successfully")
                    print("\nNote: Please install the program for easier access next time")
                    return True
                except Exception as e:
                    print(f"Error opening installer: {e}")
                    return False
            else:
                print(f"Installer not found at: {imager_path}")
                print("\nPlease install Raspberry Pi Imager first")
                return False

    elif detector.is_linux():
        print("Searching for installed Raspberry Pi Imager on Linux...")
        found_paths = search_linux_program("rpi-imager")

        if found_paths:
            print(f"Found at: {found_paths[0]}")
            print("Opening Raspberry Pi Imager...")
            try:
                subprocess.Popen([found_paths[0]])
                print("Raspberry Pi Imager opened successfully")
                return True
            except Exception as e:
                print(f"Error opening imager: {e}")
                return False
        else:
            print("Raspberry Pi Imager not found")
            print("Please install it using your package manager:")
            print("  sudo apt install rpi-imager  # Debian/Ubuntu")
            print("  sudo dnf install rpi-imager  # Fedora")
            return False

    elif detector.is_macos():
        print("Searching for installed Raspberry Pi Imager on macOS...")
        found_paths = search_macos_program("Raspberry Pi Imager")

        if found_paths:
            print(f"Found at: {found_paths[0]}")
            print("Opening Raspberry Pi Imager...")
            try:
                subprocess.Popen(['open', found_paths[0]])
                print("Raspberry Pi Imager opened successfully")
                return True
            except Exception as e:
                print(f"Error opening imager: {e}")
                return False
        else:
            print("Raspberry Pi Imager not found")
            print("\nTrying alternative: checking Downloads folder...")

            # Fallback: Check Downloads folder
            downloads = os.path.join(os.environ.get('HOME', ''), 'Downloads')
            imager_path = Path(downloads) / "rpi-imager-latest.dmg"

            if imager_path.exists():
                print(f"Found installer at: {imager_path}")
                print("Opening installer...")
                try:
                    subprocess.Popen(['open', str(imager_path)])
                    print("Installer opened successfully")
                    return True
                except Exception as e:
                    print(f"Error opening installer: {e}")
                    return False
            else:
                print("Installer not found")
                return False

    print("=" * 60)
    return False
