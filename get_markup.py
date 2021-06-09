from requests_handling import *
import configparser
from os.path import dirname, realpath

dir_of_file = 'D:\darknet_fender_protection'
dir_of_file = dir_of_file.replace("\\", '/')

# Reading Config.Txt file
config = configparser.RawConfigParser()
configFilePath = dir_of_file + '/conf.txt'
config.readfp(open(configFilePath))

camera_id_1 = config.get('camera_1', 'param_id')
camera_id_2 = config.get('camera_2', 'param_id')
camera_id_3 = config.get('camera_3', 'param_id')
camera_id_4 = config.get('camera_4', 'param_id')


def save_image(pil_image, name_for_file, camera_id):
    """ ----------------------------------------------
        this function saves the PNG format PIL image obtained from GET link
        for each cam_ID.

        ARGUMENT    :
                camera_id : cam for which Image obtained
                name_for_file : file name (markup/snapshot)
                pil_image: Image in PIL_PNG format

        RETURN      : None
        ------------------------------------------- """
    ref_dir = dir_of_file + '/ship/reference_files/'
    if not os.path.isdir(ref_dir):
        oldmask = os.umask(000)
        os.makedirs(ref_dir, 0o0777)
        os.umask(oldmask)
    # Resize image to project standard in conf.txt
    pil_image = pil_image.resize((WIDTH, HEIGHT))
    pil_image.save(ref_dir+name_for_file+'_'+str(camera_id)+'.jpg')


def get_markup_image(cameraID):
    """ -------------------------------------------------------------
    this function fetches the markup image for the camera ID provided.
    (Uses above 'save image' function to save image at location)
    ARGUMENT    : camera id
    RETURN      : if FETCHED/EXISTS : True , else: False/0
    -------------------------------------------------------------- """
    markup_cam_1 = markup_base_url+str(cameraID)
    print(markup_cam_1)
    file_name = dir_of_file + '/ship/reference_files/markup_'+str(cameraID)+'.jpg'
    if os.path.isfile(file_name):
        # if File Exists no need to fetch
        return True
    else:
        try:
            r = requests.get(markup_cam_1, stream=True).raw
            if r.status == 200:
                img = Image.open(r).convert('RGB')
                save_image(img, name_for_file='markup', camera_id=cameraID)
                return True
            else:
                return False
        except:
            print('ERROR  GET Request FAILED for markup image for Camera ID : %(id)s' % {'id': cameraID})
            return 0


get_markup_image(camera_id_1)
get_markup_image(camera_id_2)
get_markup_image(camera_id_3)
get_markup_image(camera_id_4)