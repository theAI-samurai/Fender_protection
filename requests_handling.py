from read_config import *
from PIL import Image
import requests


def get_markup_image(cameraID):
    """ --------------
    this function fetches the markup image for the camera ID provided.

    ARGUMENT    : camera id
    RETURN      : markup_image
    --------------- """
    markup_cam_1 = markup_base_url.strip("'")+str(cameraID)
    r = requests.get(markup_cam_1, stream=True).raw
    if r.status == 200:
        print('success')
        img = Image.open(r).convert('RGB')
        return img
