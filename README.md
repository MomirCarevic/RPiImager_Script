# [WIP] Script for easier flashing of Raspberry Pi OS

## Prerequisites for running this script on a Linux machine

Common with newer Ubuntu/Debian systems is that they are using externaly-managed Python environments. The best practice is to create a virtual environment for your porject. To create virtual environment you will need to run command:

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