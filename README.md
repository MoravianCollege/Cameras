# Cameras

**Requirements:**

* [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose.git "OpenPose GitHub Repository") installed in the same directory as this repository. OpenPose should be built with the BUILD_PYTHON option selected if running on Windows.
* [Python 3](https://www.python.org/downloads/ "Python Download") (preferably 3.7.4 or the latest Python 3 release).
* Windows or MacOS. Preference towards Windows 10 with a dedicated graphics card.


**Run on Boot on Windows:**

In order to have the program run on boot, place a shortcut to the program in the startup folder.
* First press `Win+R`, the Windows key and R. This will open the Run dialogue.
* Type `shell:startup` in the entry and press okay. If you want the program to run on boot for all users, type `shell:Common Startup` and hit okay.
* Open another File Explorer window and navigate to the repository. In the `src/Cameras` folder there is the program `main.py`. Right click this and choose copy.
* Finally, right click in the other File Explorer window for startup and choose paste shortcut.


**Usage:**

* Clone this repository.
* Install the required libraries with `pip3 install -r requirements.txt`, after navigating to the repository.
* Install the repository with `pip3 install -e .`
* Run main.py with `python3 src/Cameras/main.py` from the root of the repository.
* Follow in-app instructions from there.
