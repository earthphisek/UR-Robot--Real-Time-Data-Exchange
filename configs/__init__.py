import configparser
from sys import path as root_path
from os import path

CONFIG = configparser.ConfigParser()
ANTO_CONFIG = configparser.ConfigParser()
CURRENT_PATH = path.join(root_path[0], 'configs')


class BrokerConfig:
    ANTO_CONFIG.read_file(open(path.join(CURRENT_PATH, 'anto.cfg')))
    Username = ANTO_CONFIG.get(section='CONNECTION', option='Username')
    Key = ANTO_CONFIG.get(section='CONNECTION', option='Key')
    Thing = ANTO_CONFIG.get(section='CONNECTION', option='Thing')
    Broker = ANTO_CONFIG.get(section='CONNECTION', option='Broker')

    @staticmethod
    def __setattr__(name, value):
        ''' Overridden __setattr__ method to update configuration file when new attribute got updated'''
        if name in BrokerConfig.__dict__.keys():
            ANTO_CONFIG.set(section='CONNECTION', option=name, value=value)
            with open(path.join(CURRENT_PATH, 'config.cfg'), 'w') as configfile:
                ANTO_CONFIG.write(configfile)
            BrokerConfig.Username = ANTO_CONFIG.get(section='CONNECTION', option='Username')
            BrokerConfig.Key = ANTO_CONFIG.get(section='CONNECTION', option='Key')
            BrokerConfig.Thing = ANTO_CONFIG.get(section='CONNECTION', option='Thing')
            BrokerConfig.Broker = ANTO_CONFIG.get(section='CONNECTION', option='Broker')
        else:
            raise Exception('Has no attribute.')

class MQTTConfig:
    CONFIG.read_file(open(path.join(CURRENT_PATH, 'mqtt.conf')))
    Broker = CONFIG.get(section='CONNECTION', option='Broker')
    Port = CONFIG.get(section='CONNECTION', option='Port')
    Keepalive = CONFIG.get(section='CONNECTION', option='Keepalive')
    Qos = CONFIG.get(section='CONNECTION', option='Qos')
    Username = CONFIG.get(section='CONNECTION', option='Username')
    Password = CONFIG.get(section='CONNECTION', option='Password')
    SubTopics = dict(CONFIG['SUBTOPICS'])
    PubTopics = dict(CONFIG['PUBTOPICS'])

    @staticmethod
    def __setattr__(name, value):
        ''' Overridden __setattr__ method to update configuration file when
            new attribute got updated. '''
        if name in MQTTConfig.__dict__.keys():
            CONFIG.set(section='CONNECTION', option=name, value=value)
            with open(path.join(CURRENT_PATH, 'mqtt.conf'), 'w') as configfile:
                CONFIG.write(configfile)
            MQTTConfig.Broker = CONFIG.get(section='CONNECTION', option='Broker')
            MQTTConfig.Port = CONFIG.get(section='CONNECTION', option='Port')
            MQTTConfig.Keepalive = CONFIG.get(section='CONNECTION', option='Keepalive')
            MQTTConfig.Qos = CONFIG.get(section='CONNECTION', option='Qos')
            MQTTConfig.Username = CONFIG.get(section='CONNECTION', option='Username')
            MQTTConfig.Password = CONFIG.get(section='CONNECTION', option='Password')
        else:
            raise Exception('Has no attribute.')

class CalibrateConfig:
    __lines = ''
    __lines_dict = {}
    with open(path.join(CURRENT_PATH, 'calibrate.conf'), 'r') as f:
        __lines = f.readlines()
    __lines = list(map(lambda s: s.replace('\n', ''), __lines))
    for line in __lines:
        if not '=' in line:
            continue
        line = line.split('=')
        __lines_dict[line[0]] = line[1]
    FocalLength = float(__lines_dict['FOCAL_LENGTH'])
    ScaleFactor = float(__lines_dict['SCALE_FACTOR'])
    ObjectWidth = float(__lines_dict['OBJECT_WIDTH'])
    CaptureWidth = int(__lines_dict['CAPTURE_WIDTH'])
    CaptureHeight = int(__lines_dict['CAPTURE_HEIGHT'])
    CaptureId = int(__lines_dict['CAPTURE_ID'])
