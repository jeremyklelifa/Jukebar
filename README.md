# README

This is just my hello world project.

## Install dependencies

### Windows
Tested under Windows 7 & Windows 10.

	pip install -r requirements/windows.txt

### Linux
Tested under Ubuntu Xenial 16.04.

    apt install mesa-common-dev libgl1-mesa-dev libsmpeg0
	pip install -r requirements/linux.txt

### Android
Tested under Android 6.0.

    pip install -r requirements/android.txt

## Run or deploy
On Windows and Linux, go to the Jukebar/ directory and run:

    python Jukebar/main.py

To deploy on Android, go to the Jukebar/ directory and run:

    buildozer android_new debug deploy run
