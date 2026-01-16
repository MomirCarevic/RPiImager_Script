#!/usr/bin/env python3
"""
Make Files Module
Creates necessary files (ssh, userconf) for Raspberry Pi boot configuration.
"""

from pathlib import Path


def create_bootfs_folder(drive_mountpoint):
    """Create bootfs folder if it doesn't exist."""
    bootfs_path = Path(drive_mountpoint) / "bootfs"

    try:
        bootfs_path.mkdir(parents=True, exist_ok=True)
        print(f"bootfs folder ready at: {bootfs_path}")
        return bootfs_path
    except Exception as e:
        print(f"Error creating bootfs folder: {e}")
        return None


def create_ssh_file(bootfs_path):
    """Create empty ssh file without extension."""
    ssh_file = bootfs_path / "ssh"

    try:
        # Create empty file
        ssh_file.touch()
        print(f"Created ssh file at: {ssh_file}")
        return True
    except Exception as e:
        print(f"Error creating ssh file: {e}")
        return False


def create_userconf_file(bootfs_path):
    """Create empty userconf file without extension."""
    userconf_file = bootfs_path / "userconf"

    try:
        # Create empty file
        userconf_file.touch()
        print(f"Created userconf file at: {userconf_file}")
        return True
    except Exception as e:
        print(f"Error creating userconf file: {e}")
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
    print("CREATING BOOT CONFIGURATION FILES")
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

    # Create bootfs folder
    bootfs_path = create_bootfs_folder(selected_drive.mountpoint)
    if not bootfs_path:
        return False

    # Create ssh file
    ssh_created = create_ssh_file(bootfs_path)

    # Create userconf file
    userconf_created = create_userconf_file(bootfs_path)

    print("=" * 60)

    if ssh_created and userconf_created:
        print("\nAll boot configuration files created successfully!")
        print(f"\nFiles created in: {bootfs_path}")
        print("  - ssh (enables SSH on first boot)")
        print("  - userconf (user configuration file)")
        return True
    else:
        print("\nSome files could not be created")
        return False


if __name__ == "__main__":
    # Test the file creation
    print("This module creates boot configuration files for Raspberry Pi")
    print("Run the main script (run.py) to use this functionality")
