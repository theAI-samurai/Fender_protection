import configparser
from os.path import dirname, realpath

dir_of_file = dirname(realpath(__file__))

# Reading Config.Txt file
config = configparser.RawConfigParser()
configFilePath = dir_of_file + '/conf.txt'
config.readfp(open(configFilePath))

# Extracting fields and values for cameras
camera_1_path = config.get('camera_1', 'feeder_path')
camera_1_id = config.get('camera_1', 'param_id')

# Extracting fields for Requests
notification_url = config.get('GET_POST_URL', 'notification')
markup_base_url = config.get('GET_POST_URL', 'markup')






