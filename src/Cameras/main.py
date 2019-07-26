from argparse import ArgumentParser
from Cameras.gui_manager import GUIManager

# Get video flag
parser = ArgumentParser()
parser.add_argument('--video', default='0', dest='video', type=str, help='The path to a video or number of the camera used for capture.')
video = parser.parse_args().video
try:
    video = int(video)
except ValueError:
    pass

manager = GUIManager(camera_source=video)
manager.get_alert_sound()
manager.run_gui()
