#!/usr/bin/env python3
"""
Raspberry Pi Imager Download Module
Downloads the latest Raspberry Pi Imager based on the operating system.
"""

import requests
import os
import sys
from pathlib import Path
from .detect_os import OSDetector


class ImagerDownloader:
    """Downloads the appropriate Raspberry Pi Imager for the current OS."""

    # Official Raspberry Pi Imager download URLs
    IMAGER_URLS = {
        "Windows": "https://downloads.raspberrypi.org/imager/imager_latest.exe",
        "Linux": "https://downloads.raspberrypi.org/imager/imager_latest_amd64.deb",
        "Darwin": "https://downloads.raspberrypi.org/imager/imager_latest.dmg"
    }

    # Alternative URLs for different Linux distributions
    LINUX_VARIANTS = {
        "deb": "https://downloads.raspberrypi.org/imager/imager_latest_amd64.deb",
        "rpm": "https://downloads.raspberrypi.org/imager/imager_latest.rpm",
        "appimage": "https://downloads.raspberrypi.org/imager/imager_latest.AppImage"
    }

    def __init__(self, detector=None):
        """Initialize the downloader with OS detection."""
        self.detector = detector if detector else OSDetector()
        self.os_type = self.detector.get_os_type()
        self.download_dir = self._get_system_downloads_folder()

    def _get_system_downloads_folder(self):
        """Get the system's Downloads folder path."""
        if self.detector.is_windows():
            # Windows: Use USERPROFILE environment variable
            downloads = os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads')
        elif self.detector.is_macos() or self.detector.is_linux():
            # macOS and Linux: Use HOME environment variable
            downloads = os.path.join(os.environ.get('HOME', ''), 'Downloads')
        else:
            # Fallback to current directory
            downloads = 'downloads'

        return Path(downloads)

    def get_download_url(self, linux_variant="deb"):
        """Get the appropriate download URL for the current OS."""
        if self.os_type == "Linux":
            return self.LINUX_VARIANTS.get(linux_variant, self.LINUX_VARIANTS["deb"])
        return self.IMAGER_URLS.get(self.os_type)

    def get_filename(self, linux_variant="deb"):
        """Get the appropriate filename for the downloaded file."""
        if self.detector.is_windows():
            return "rpi-imager-latest.exe"
        elif self.detector.is_macos():
            return "rpi-imager-latest.dmg"
        elif self.detector.is_linux():
            extensions = {
                "deb": ".deb",
                "rpm": ".rpm",
                "appimage": ".AppImage"
            }
            return f"rpi-imager-latest{extensions.get(linux_variant, '.deb')}"
        return "rpi-imager-latest"

    def create_download_directory(self):
        """Create the downloads directory if it doesn't exist."""
        self.download_dir.mkdir(exist_ok=True)
        print(f"Download directory: {self.download_dir.absolute()}")

    def download_file(self, url, filename, chunk_size=8192):
        """Download a file with progress indication."""
        filepath = self.download_dir / filename

        print(f"Downloading from: {url}")
        print(f"Saving to: {filepath.absolute()}")

        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # Show progress
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\rProgress: {progress:.1f}% ({downloaded_size}/{total_size} bytes)", end='')
                        else:
                            print(f"\rDownloaded: {downloaded_size} bytes", end='')

            print("\nDownload completed successfully!")
            return filepath

        except requests.exceptions.RequestException as e:
            print(f"\nError downloading file: {e}")
            return None
        except IOError as e:
            print(f"\nError saving file: {e}")
            return None

    def download_imager(self, linux_variant="deb"):
        """Main method to download Raspberry Pi Imager."""
        print("=" * 60)
        print("RASPBERRY PI IMAGER DOWNLOADER")
        print("=" * 60)
        print(f"Detected OS: {self.os_type}")

        # Check if OS is supported
        url = self.get_download_url(linux_variant)
        if not url:
            print(f"Unsupported operating system: {self.os_type}")
            return None

        # Create download directory
        self.create_download_directory()

        # Get filename
        filename = self.get_filename(linux_variant)

        # Check if file already exists
        filepath = self.download_dir / filename
        if filepath.exists():
            print(f"\nFile already exists: {filepath.absolute()}")
            response = input("Do you want to re-download? (y/n): ").lower()
            if response != 'y':
                print("Using existing file.")
                return filepath

        # Download the file
        print(f"\nDownloading Raspberry Pi Imager for {self.os_type}...")
        downloaded_file = self.download_file(url, filename)

        if downloaded_file:
            print(f"\n{'=' * 60}")
            print("INSTALLATION INSTRUCTIONS")
            print("=" * 60)
            self._print_installation_instructions(downloaded_file)

        return downloaded_file

    def _print_installation_instructions(self, filepath):
        """Print OS-specific installation instructions."""
        if self.detector.is_windows():
            print("\nWindows Installation:")
            print(f"  1. Double-click: {filepath.absolute()}")
            print("  2. Follow the installation wizard")
            print("  3. Run as Administrator when flashing SD cards")

        elif self.detector.is_linux():
            if filepath.suffix == ".deb":
                print("\nDebian/Ubuntu Installation:")
                print(f"  sudo dpkg -i {filepath.absolute()}")
                print("  sudo apt-get install -f  # If dependencies are missing")
            elif filepath.suffix == ".rpm":
                print("\nFedora/RHEL Installation:")
                print(f"  sudo rpm -i {filepath.absolute()}")
            elif filepath.suffix == ".AppImage":
                print("\nAppImage Usage:")
                print(f"  chmod +x {filepath.absolute()}")
                print(f"  ./{filepath.name}")

        elif self.detector.is_macos():
            print("\nmacOS Installation:")
            print(f"  1. Double-click: {filepath.absolute()}")
            print("  2. Drag Raspberry Pi Imager to Applications folder")
            print("  3. Run with 'sudo' when flashing SD cards")

        print(f"\n{'=' * 60}")


def download_raspberry_pi_imager(linux_variant="deb"):
    """Convenience function to download Raspberry Pi Imager."""
    detector = OSDetector()
    downloader = ImagerDownloader(detector)
    return downloader.download_imager(linux_variant)


if __name__ == "__main__":
    # Allow specifying Linux variant as command-line argument
    linux_variant = "deb"
    if len(sys.argv) > 1:
        linux_variant = sys.argv[1].lower()

    download_raspberry_pi_imager(linux_variant)
