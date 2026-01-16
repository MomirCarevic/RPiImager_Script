#!/usr/bin/env python3
"""
Raspberry Pi Imager Script - Main Entry Point
"""

from utils.detect_os import detect_and_display
from utils.download_imager import download_raspberry_pi_imager
from utils.open_raspberrypi_imager import open_imager, is_imager_installed
from utils.monitor_imager import monitor_and_wait
from utils.select_drive import select_drive
from utils.make_files import make_files
from utils.utils import clear_screen


def main():
    """Main function to run the Raspberry Pi Imager Script."""
    # Detect and display OS information
    detector = detect_and_display()

    clear_screen()
    print("=" * 60)
    print("STEP 1 : CHECKING RASPBERRY PI IMAGER INSTALLATION")
    print("=" * 60)

    # Check if Raspberry Pi Imager is already installed
    if is_imager_installed():
        print("\nRaspberry Pi Imager is already installed on this system")
        print("=" * 60)
        print("STEP 2 : FLASH YOUR SD CARD")
        print("=" * 60)
        print("\nstarting Raspberry Pi Imager ...")
        print("\n\n\n\n\nThe script will wait for you to complete the flashing...")
        print("=" * 60)

        open_imager()

        # Monitor the Raspberry Pi Imager process until it closes
        monitor_and_wait()

        # After flashing is complete, select the drive to add files
        clear_screen()
        print("=" * 60)
        print("STEP 3 : SELECT THE FLASHED DRIVE")
        print("=" * 60)
        print("Now that flashing is complete, please select the drive")
        print("where you want to add additional files.")
        print("=" * 60)

        
        print("\tHeadless boot only works durign first boot and ")
        print("\tis used when you boot via ssh with no moniutor, ")
        print("\tkeyboard nor mouse.")
        confirm = input("\n\nDo you need headless boot? (y/n): ")

        if confirm == 'y':
            selected_drive = select_drive()

            if not selected_drive:
                print("\nNo drive selected. Exiting.")
                return

            print("\n" + "=" * 60)
            print("DRIVE SELECTED FOR FILE OPERATIONS")
            print("=" * 60)
            print(f"Selected Drive: {selected_drive.device}")
            print(f"Mount Point: {selected_drive.mountpoint}")
            print(f"Size: {selected_drive.size / (1024**3):.2f} GB")
            print(f"File System: {selected_drive.fstype}")
            if selected_drive.label:
                print(f"Label: {selected_drive.label}")
            print("=" * 60)
            # Create boot configuration files
            print("\n")
            print("=" * 60)
            print("STEP 4 : CREATE HEADLESS BOOT CONFIGURATION FILES")
            print("=" * 60)

            success = make_files(selected_drive)

            if success:
                print("\n" + "=" * 60)
                print("SETUP COMPLETE!")
                print("=" * 60)
                print("Your Raspberry Pi SD card is now ready to use.")
                print("You can safely eject the SD card and insert it into your Raspberry Pi.")
                return
            
            else:
                print("\nFailed to create all boot configuration files")
                print("You may need to create them manually")

        elif confirm == 'n' :
            print("\n" + "=" * 60)
            print("SETUP COMPLETE!")
            print("=" * 60)
            print("Your Raspberry Pi SD card is now ready to use.")
            print("You can safely eject the SD card and insert it into your Raspberry Pi.")

            return

    print("Raspberry Pi Imager is not installed on this system")

    # Ask user if they want to download and install
    print("\n")
    response = input("Would you like to download the Raspberry Pi Imager installer? (y/n): ").lower()

    if response != 'y':
        print("\nExiting without downloading.")
        return

    # Download Raspberry Pi Imager
    print("\n")
    downloaded_file = download_raspberry_pi_imager()

    if downloaded_file:
        print(f"\nRaspberry Pi Imager installer ready at: {downloaded_file}")
        print("\n")

        # Ask if they want to open the installer now
        install_response = input("Would you like to open the installer now? (y/n): ").lower()

        if install_response == 'y':
            open_imager()
            print("\nPlease install Raspberry Pi Imager and run this script again")
        else:
            print(f"\nYou can install it later by running the file at: {downloaded_file}")
    else:
        print("\nFailed to download Raspberry Pi Imager")
        return


if __name__ == "__main__":
    main()
