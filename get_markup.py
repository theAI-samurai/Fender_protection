from requests_handling import *
import configparser
from os.path import dirname, realpath

dir_of_file = dirname(realpath(__file__))
dir_of_file = dir_of_file.replace("\\", '/')

# Reading Config.Txt file
config = configparser.RawConfigParser()
configFilePath = dir_of_file + '/conf.txt'
config.readfp(open(configFilePath))


camera_id_1 = config.get('camera_1', 'param_id')
camera_id_2 = config.get('camera_2', 'param_id')
camera_id_3 = config.get('camera_3', 'param_id')
camera_id_4 = config.get('camera_4', 'param_id')


get_markup_image(camera_id_1)
get_markup_image(camera_id_2)
get_markup_image(camera_id_3)
get_markup_image(camera_id_4)