#!/usr/bin/env python3
"""
Make Files Module
Creates necessary files (ssh, userconf) for Raspberry Pi boot configuration.
"""

import subprocess
import sys
from pathlib import Path
from getpass import getpass


def create_ssh_file(drive_path):
    """Create empty ssh file without extension."""
    ssh_file = drive_path / "ssh"

    try:
        # Create empty file
        ssh_file.touch()
        print(f"Created ssh file at: {ssh_file}")
        return True
    except Exception as e:
        print(f"Error creating ssh file: {e}")
        return False


def create_userconf_file(drive_path):
    """Create empty userconf file without extension."""
    userconf_file = drive_path / "userconf"

    try:
        # Create empty file
        userconf_file.touch()
        print(f"Created userconf file at: {userconf_file}")
        return True
    except Exception as e:
        print(f"Error creating userconf file: {e}")
        return False


def check_openssl_installed():
    """Check if OpenSSL is installed and available."""
    try:
        result = subprocess.run(
            ["openssl", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def install_openssl_chocolatey():
    """Attempt to install OpenSSL using Chocolatey."""
    print("\nAttempting to install OpenSSL via Chocolatey...")
    print("Note: This requires administrator privileges")

    try:
        # Check if chocolatey is installed
        choco_check = subprocess.run(
            ["choco", "--version"],
            capture_output=True,
            shell=True,
            timeout=5
        )

        if choco_check.returncode != 0:
            print("Error: Chocolatey is not installed")
            print("Install Chocolatey from: https://chocolatey.org/install")
            return False

        # Install OpenSSL
        print("Installing OpenSSL... This may take a few minutes.")
        result = subprocess.run(
            ["choco", "install", "openssl", "-y"],
            shell=True,
            timeout=300
        )

        if result.returncode == 0:
            print("OpenSSL installed successfully!")
            # Refresh environment variables
            print("Refreshing PATH...")
            return True
        else:
            print("Failed to install OpenSSL via Chocolatey")
            return False

    except subprocess.TimeoutExpired:
        print("Installation timed out")
        return False
    except Exception as e:
        print(f"Error during installation: {e}")
        return False


def encrypt_password_with_openssl(password):
    """Encrypt password using OpenSSL. Returns encrypted password or None."""
    try:
        result = subprocess.run(
            ["openssl", "passwd", "-6", password],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        return result.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def add_user_to_userconf(drive_path):
    """
    Add username and encrypted password to userconf file.
    Format: username:encrypted_password
    """
    userconf_file = drive_path / "userconf"

    try:
        # Get username from user
        print("\n--- User Configuration ---")
        username = input("Enter username for Raspberry Pi: ").strip()

        if not username:
            print("Error: Username cannot be empty")
            return False

        # Get password from user (hidden input)
        password = getpass("Enter password: ").strip()

        if not password:
            print("Error: Password cannot be empty")
            return False

        # Confirm password
        password_confirm = getpass("Confirm password: ").strip()

        if password != password_confirm:
            print("Error: Passwords do not match")
            return False

        # Encrypt password using openssl
        print("Encrypting password...")
        encrypted_password = encrypt_password_with_openssl(password)

        # If encryption failed, check if OpenSSL is installed
        if encrypted_password is None:
            if not check_openssl_installed():
                print("\nOpenSSL is not installed or not found in PATH")
                print("\nInstallation options:")
                print("1. Install via Chocolatey (automatic)")
                print("2. Download and install manually")
                print("3. Cancel")

                install_choice = input("\nSelect an option (1/2/3): ").strip()

                if install_choice == '1':
                    # Install via Chocolatey
                    if install_openssl_chocolatey():
                        # Retry encryption after installation
                        print("\nRetrying password encryption...")
                        encrypted_password = encrypt_password_with_openssl(password)

                        if encrypted_password is None:
                            print("Error: Still cannot encrypt password after installation")
                            print("You may need to restart your terminal/script")
                            return False
                    else:
                        return False

                elif install_choice == '2':
                    # Manual installation
                    print("\n" + "=" * 60)
                    print("MANUAL INSTALLATION REQUIRED")
                    print("=" * 60)
                    print("\n1. Download OpenSSL from:")
                    print("   https://slproweb.com/products/Win32OpenSSL.html")
                    print("\n2. Download 'Win64 OpenSSL v3.x.x' (not the Light version)")
                    print("\n3. Run the installer and follow the installation wizard")
                    print("\n4. Make sure to add OpenSSL to the system PATH when prompted")
                    print("\n5. After installation, you may need to restart your terminal")
                    print("=" * 60)

                    input("\nPress Enter when you have completed the installation...")

                    # Check if OpenSSL is now available
                    print("\nChecking for OpenSSL installation...")
                    if check_openssl_installed():
                        print("OpenSSL found! Continuing...")
                        # Retry encryption after installation
                        print("Encrypting password...")
                        encrypted_password = encrypt_password_with_openssl(password)

                        if encrypted_password is None:
                            print("\nError: Still cannot encrypt password")
                            print("Please make sure OpenSSL was added to your PATH")
                            print("You may need to restart your terminal or computer")
                            return False
                    else:
                        print("\nError: OpenSSL still not found in PATH")
                        print("\nTroubleshooting:")
                        print("1. Make sure you selected 'Add to PATH' during installation")
                        print("2. Restart your terminal/command prompt")
                        print("3. If still not working, restart your computer")
                        print("\nAlternative: Run this script in Git Bash or WSL")
                        return False

                else:
                    print("\nCannot proceed without OpenSSL")
                    print("Installation cancelled by user")
                    return False
            else:
                print("Error: Failed to encrypt password")
                return False

        # Create userconf content
        userconf_content = f"{username}:{encrypted_password}\n"

        # Write to file
        userconf_file.write_text(userconf_content, encoding='utf-8')
        print(f"Added user configuration to: {userconf_file}")
        print(f"Username: {username}")
        return True

    except Exception as e:
        print(f"Error adding user to userconf file: {e}")
        return False


def make_files(selected_drive):
    """
    Create necessary boot configuration files on the selected drive.

    Args:
        selected_drive: DriveInfo object containing drive information

    Returns:
        bool: True if all files were created successfully, False otherwise
    """
    print("\n" + "=" * 60)
    print("CREATING HEADLESS BOOT CONFIGURATION FILES")
    print("=" * 60)

    if not selected_drive:
        print("No drive selected")
        return False

    if not selected_drive.mountpoint:
        print(f"Drive {selected_drive.device} is not mounted")
        print("Please ensure the drive is mounted before creating files")
        return False

    print(f"Target drive: {selected_drive.device}")
    print(f"Mount point: {selected_drive.mountpoint}")

    # Get drive path
    drive_path = Path(selected_drive.mountpoint)

    # Create ssh file
    ssh_created = create_ssh_file(drive_path)

    # Create userconf file
    userconf_created = create_userconf_file(drive_path)

    if not (ssh_created and userconf_created):
        print("\nSome files could not be created")
        print("=" * 60)
        return False

    # Add user configuration to userconf file
    user_added = add_user_to_userconf(drive_path)

    print("=" * 60)

    if user_added:
        print("\nAll boot configuration files created successfully!")
        print(f"\nFiles created in: {drive_path}")
        print("  - ssh (enables SSH on first boot)")
        print("  - userconf (user configuration file)")
        return True
    else:
        print("\nFailed to add user configuration")
        return False


if __name__ == "__main__":
    # Test the file creation
    print("This module creates boot configuration files for Raspberry Pi")
    print("Run the main script (run.py) to use this functionality")
