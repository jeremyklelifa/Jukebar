# Jukebar

Jukebox for the drinkers.

## Install dependencies

### Windows
Tested under Windows 7 & Windows 10.

	pip install -r requirements/windows.txt
    garden install recycleview

### Linux
#### Ubuntu Xenial 16.04

    apt install mesa-common-dev libgl1-mesa-dev libsmpeg0 python-gst-1.0
	pip install -r requirements/linux.txt
    garden install recycleview

#### Gentoo

    emerge media-libs/mesa media-libs/smpeg dev-python/gst-python media-plugins/gst-plugins-meta

### Android
Tested under Android 6.0.

    pip install -r requirements/android.txt
    garden install recycleview

## Run or deploy
On Windows and Linux, go to the Jukebar/ directory and run:

    python Jukebar/main.py

To deploy on Android, go to the Jukebar/ directory and run:

    buildozer android_new debug deploy run
