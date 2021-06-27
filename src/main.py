import platform
from os.path import abspath, dirname
from pathlib import Path

from src.utils.dataclass import GestureMetaData
from gesture_capturing import GestureCapture

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parent_directory = dirname(dirname(abspath(__file__)))
    print(parent_directory)
    parent_directory = Path(parent_directory)
    path = parent_directory / "Akash"
    gestureMetaData = GestureMetaData(gesture_name="gesture_l_down_15")

    if platform.system() == "Darwin":  # for me on mac input 1 is the camera
        gesture = GestureCapture(folder_location=str(path), gesture_meta_data=gestureMetaData, camera_input_value=1)
    else:
        gesture = GestureCapture(folder_location=str(path), gesture_meta_data=gestureMetaData, camera_input_value=0)

    gesture.get_frame()

