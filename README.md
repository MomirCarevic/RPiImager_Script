# [WIP] Script for easier flashing of Raspberry Pi OS

This script automates proces of downloading Raspberry Pi Imager, running the imager and preparing SD card for headless boot.
## Prerequisites for running this script on a **Windows** machine

For this script to make headless boot work, password is encripted via openssl. Windows machines don't have installed OpenSSL and because of that you will need to install OpenSSL from [Shining Light Productions](https://slproweb.com/products/Win32OpenSSL.html) website or to use command:

    choco install openssl -y

After installing openssl, system must know where openssl.exe is located. 
Find your OpenSSL bin folder (usually *C:\Program Files\OpenSSL-Win64\bin* or *C:\Program Files\Git\usr\bin*).


## Prerequisites for running this script on a **Linux** machine
Common with newer Ubuntu/Debian systems is that they are using externaly-managed Python environments. The best practice is to create a virtual environment for your porject. To create virtual environment you will need to run command:

    ./econ_linux.sh

If you want to do it manualy, follow next steps. Run command:

    python3 -m venv venv

and then install dependencies in the virtual environment:

    venv/bin/pip install -r requirements.txt

Now you can run your script using virtual environment's Python:

    venv/bin/python3 run.py

Alternatively, you can activate the virtual environment first and then run the script normally:

    source venv/bin/activate
    python3 run.py

When you're done working, you can deactivate the virtual environment with:

    deactive

The virtual environment (venv folder) has been created in your project directory and contains all the required dependencies.