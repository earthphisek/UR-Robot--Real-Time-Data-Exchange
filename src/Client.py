import random, string
from rich.console import Console
from rich.traceback import install

console = Console()
install()

from configs import MQTTConfig
import paho.mqtt.client as mqtt
from collections.abc import Callable
from typing import Union

MQTT_CONF = MQTTConfig()

class Client:
    def __init__(self, 
            broker:str=MQTT_CONF.Broker,
            port:int=int(MQTT_CONF.Port),
            subs:dict=MQTT_CONF.SubTopics,
            pubs:dict=MQTT_CONF.PubTopics,
            username:str=MQTT_CONF.Username,
            password:str=MQTT_CONF.Password,
            qos:int=int(MQTT_CONF.Qos),
            keepalive:int=int(MQTT_CONF.Keepalive),
            on_data_fnc:Callable=None,
            verbose:bool=False):
        # TODO : Ignore first subcribe
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.qos = qos
        self.keepalive = keepalive
        self.subs = subs
        self.pubs = pubs
        self.verbose = verbose
        self.client = mqtt.Client(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        self.client.__init__
        self.client.connect(self.broker, self.port, self.keepalive)
        self.on_data_fnc = on_data_fnc if on_data_fnc != None else self.__on_data
        self.client.on_message = self.on_data_fnc
        self.subs_val = dict()
        self.cache_sub_ret = dict()
        # self.__first_sub = 0
        topics_lst = []
        for topic in self.subs.keys():
            topics_lst.append((self.subs[topic], self.qos))
            # self.__first_sub += 1
        [status, msg_id] = self.client.subscribe(topics_lst, self.qos)
        if len(self.subs) != 0:
            for ch in subs:
                self.subs_val[ch.lower()] = None
        if self.verbose:
            console.log(f'Subscribe status: {status}, with message id: {msg_id}')

    def sub(self, topics:list=[]) -> dict:
        ret_dict = dict()
        for topic in topics:
            key = None
            if len(self.subs_val) == 0:
                break
            if topic == None:
                continue
            if topic.lower() in self.subs.keys():
                key = topic.lower()
            elif topic.lower() in self.subs.values():
                key = self.__get_subs_key(topic)
            else:
                continue
            ret_dict[topic] = None
            if self.subs_val[key] != None:
                ret_dict[topic] = self.subs_val[key].decode('utf-8')
        if ret_dict == self.cache_sub_ret:
            for key in ret_dict:
                ret_dict[key] = None
        else:
            self.cache_sub_ret = ret_dict.copy()
        # if self.__first_sub > 0:
            # self.__first_sub -= 1
            # for key in ret_dict:
                # ret_dict[key] = None
        return ret_dict

    def pub(self, topics_payload_pair:dict, verbose:bool=False) -> bool:
        for topic in topics_payload_pair.keys():
            if topic.lower() in self.subs.keys():
                topic_path = self.subs[topic.lower()]
            elif topic in self.subs.values():
                topic_path = topic.lower()
            else:
                topic_path = topic
            result = self.client.publish(topic_path, topics_payload_pair[topic], self.qos, retain=True)
            if verbose:
                if result[0] == 0:
                    if self.verbose:
                        print(f'Publish to topic: {topic} successfully.')
                else:
                    if self.verbose:
                        print(f'Failed to publish to topic: {topic}, {result}.')
        return True if result == 0 else False

    def __on_data(self, mosq, obj, msg):
        payload = msg.payload
        # topic = msg.topic.split('/')[3]
        topic = msg.topic
        if payload:
            self.subs_val[str(topic).lower()] = payload
        else:
            self.subs_val[str(topic).lower()] = None

    def __get_subs_key(self, target_val:str) -> Union[str, int, None]:
        try:
            for key, val in self.subs:
                if val == target_val:
                    return key
        except Exception as e:
            console.log(e, log_locals=True)
    
    def loop_start(self) -> None:
        self.client.loop_start()

