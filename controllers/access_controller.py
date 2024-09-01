import json
import logging

from ORM.database import DatabaseConnection
from ORM.tables import VisitsHistory
from ORM.loggers import VisitLogger
from remote.tools import WebsoketClients
from hardware.setting import arduions_configuring

class AccessController:
    '''Класс для управления несолькими ардуино и взаимодействия с БД'''
    def __init__(self, skud: DatabaseConnection, ports: list[str], visits_db: VisitLogger, isdaemon: bool = True, logger: logging.Logger = None, Debug: bool = False) -> None:
        '''`skud` - класс для соединения с БД скуда, `ports` - список портов, к которым подключены устройства, 
        `visits_db` - класс для соединения с БД инофрмации, полученной от устройств, 
        `logger` - класс для сохранения ошибок и дополнительной информации'''
        self.skud = skud
        self.skud.establish_connection()
        self.visits_db = visits_db
        self.visits_db.establish_connection()

        self.arduinos_therad, self.arduinos = arduions_configuring(ports, self.arduino_handler, isdaemon=isdaemon)

        self.logger = logger
        self.Debug = Debug

    def arduino_handler(self, port: str, data: bytes, **kwargs) -> None:
        '''Обработчик приходящих с ардуино сообщений, `port` - порт, к которому подключено устройство, 
        `data` - полученные данные'''
        try: 
            msg = json.loads(data.decode('utf-8'))

            if msg["type"] == "pass":
                inserted_row = VisitsHistory(port, msg["key"])
                self.visits_db.establish_connection()
                if "key" in msg.keys():
                    check = self.visits_db.addvisit(inserted_row)
                    if check:
                        WebsoketClients().send(inserted_row.toJSON())

            #### DEBUG ####
            if self.Debug:
                if inserted_row: print(port, inserted_row.toJSON())
                else: print(port, data)

        except BaseException as error:
            if self.logger:
                self.logger.exception(f"{error}; In AccessController.arduino_handler() with port = {port} and data = {data}")
            
            #### DEBUG ####
            if self.Debug: print(error)

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
