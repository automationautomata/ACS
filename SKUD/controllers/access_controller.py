import json
from logging import Logger

from SKUD.ORM.database import DatabaseConnection
from SKUD.ORM.tables import VisitsHistory
from SKUD.ORM.connections import VisitsConnection
from SKUD.general.exception_handler import exception_handler
from SKUD.hardware.arduino import ArduinoCommunicator
from SKUD.hardware.tools import arduions_configuring
from SKUD.remote.tools import WebsoketClients


type PortLoggerMap = dict[str, Logger]
'''Ключ - порт, значение - логгер.'''

class AccessController:
    '''Класс для управления несолькими ардуино и взаимодействия с БД'''
    logger: Logger = None
    def __init__(self, skud: DatabaseConnection, ports: list[str], logger: Logger, visits_db: VisitsConnection, 
                 isdaemon: bool = True, Debug: bool = False, arduino_loggers: PortLoggerMap = None) -> None:
        '''`skud` - класс для соединения с БД скуда, `ports` - список портов, к которым подключены устройства, 
        `visits_db` - класс для соединения с БД инофрмации, полученной от устройств, 
        `logger` - класс для сохранения ошибок и дополнительной информации'''
        self.skud = skud
        self.skud.establish_connection()
        self.visits_db = visits_db
        self.visits_db.establish_connection()
        self.arduinos_therad, self.arduinos = arduions_configuring(ports, self.arduino_handler, isdaemon=isdaemon)

        AccessController.logger = logger

        for port in arduino_loggers.keys() & self.arduinos.keys():
            self.arduinos[port].logger = arduino_loggers[port]    

        self.Debug = Debug


    @exception_handler(logger)
    def arduino_handler(self, port: str, data: bytes, **kwargs) -> None:
        '''Обработчик приходящих с ардуино сообщений, `port` - порт, к которому подключено устройство, 
        `data` - полученные данные'''
        #try: 
        msg = json.loads(data.decode('utf-8'))

        if msg["type"] == "pass":
            inserted_row = VisitsHistory(port, msg["key"])
            self.visits_db.establish_connection()
            if "key" in msg.keys():
                check = self.visits_db.addvisit(inserted_row)
                if check:
                    WebsoketClients().send(inserted_row.to_json())

        #### DEBUG ####
        if self.Debug:
            if inserted_row: print(port, inserted_row.to_json())
            else: print(port, data)

        # except BaseException as error:
        #     if self.logger:
        #         self.logger.exception(f"{error}; In AccessController.arduino_handler() with port = {port} and data = {data}")
            
            #### DEBUG ####
            #if self.Debug: print(error)
    @exception_handler(logger)
    def distribute_keys(self, room_port: dict[int, str]) -> None:
        '''Распределяет ключи по устройствам. `room_port` - словарь, где ключ - комната, а занчение - название порта'''
        sql = f'''SELECT entities.card, access_rules.room from entities INNER JOIN access_rules 
                                        ON entities.right = access_rules.right
                                                    WHERE entities.date_time_end IS NULL 
                                                        AND access_rules.date_time_end IS NULL;'''
        cards = self.skud.execute_query(sql)

        #### DEBUG ####
        if self.Debug: print('\n'.join(cards))

        for room, port in room_port.items():
            msg = list(map(lambda row: row[0], filter(lambda row: row[1] == room, cards)))
            self.arduinos[port].write('{'+f"\"cards\": \"{msg}\""+'}')

    def start(self, room_port: dict[int, str]) -> None:
        '''Запустить поток обработки событий с ардуино'''
        # for ard in self.arduinos.values():
        #     ard.open()
        self.arduinos_therad.start()
        self.distribute_keys(room_port)
