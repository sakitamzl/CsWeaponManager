import pymysql
import configparser


class read_conf:
    config = None

    def __init__(self):
        # 如果配置信息尚未加载，则加载配置文件
        if not read_conf.config:
            read_conf.config = self._load_config()

    def _load_config(self):
        self.config = configparser.ConfigParser()
        self.config.read('conf.ini', encoding='utf-8')
        return self.config

    def database(self):
        host = self.config.get('database', 'host')
        port = self.config.get('database', 'port')
        port = int(port)
        user = self.config.get('database', 'user')
        password = self.config.get('database', 'password')
        database = self.config.get('database', 'database_name')
        db = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
        return db

    def http_proxy(self):
        if_true = self.config.get('http_proxy', 'true')
        host = self.config.get('http_proxy', 'host')
        port = self.config.get('http_proxy', 'port')
        proxy_url = "http://" + host + ":" + port

        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }

        # print(type(if_true))
        if if_true == "True":
            return True, proxies
        else:
            return False, proxies

    def log_level(self):
        level = self.config.get('LogLevel', 'level')
        return level

    def processes(self):
        number = self.config.get('processes', 'number')
        return number

