from configparser import ConfigParser

hosting_config_file_loc = "../config/hosting.cfg"
hosting_keys = ["common_config"]


class ConfigModule:
    __slots__ = ('class_name', 'config_obj')

    def __init__(self, class_name):
        self.class_name = class_name
        self.config_obj = ConfigParser()
        if class_name in hosting_keys:
            self.config_obj.read(hosting_config_file_loc)

    def get_config_details(self, key):
        try:
            value = ''
            if self.config_obj.has_section(self.class_name):
                value = self.config_obj.get(self.class_name, key, fallback='')
            return value
        except Exception as e:
            raise Exception("config_reading_error" + str(e))