import asyncio
from datetime import datetime
import logging
from typing import Any, Callable
import schedule
import serial
import serial.tools.list_ports

class ArduinoCommunicator:
    '''Класс для отправки данных на ардуино'''
    def __init__(self, port: str, handler: Callable[[str, bytes, Any], str], handler_kwargs = None, startflag: str = "{", endflag: str = "}", 
                 format_send: Callable[[Any], str] = None, logger: logging.Logger = None, baudrate: int = 9600) -> None:
        '''`port` - номер COM порта, `format_send` - функция, превращающая входные данные в строку, 
        `logger` - сохраняет ошибки и доп.информацию в БД, `baudrate` - частота'''
        self.connection = serial.Serial(port, baudrate)
        self.logger = logger
        self.handler = handler
        self.format_send = format_send
        self.endflag = endflag
        self.startflag = startflag
        self.deffered_tags = set()
        self.handler_kwargs = handler_kwargs
        #### self.format_receive = format_receive - нужно ???
    
    def open(self):
        '''ОТкрывает соединение'''
        self.connection.open()

    def deffered_write(self, data: str, datetime: datetime) -> None:
        '''Отложенная запись в ардуино. `data` - данные, `datetime` - время, в которое нужно сделать запись'''
        def job(tag): 
            self.write(data)
            self.deffered_tags.remove(str(datetime))
            return schedule.CancelJob
        self.deffered_tags.add(str(datetime))
        schedule.every().day.at(str(datetime)).do(job, str(datetime)).tag(str(datetime))

    def cancel_deffered_write(self, datetime: datetime) -> bool:
        '''Отменить отложенную запись в ардуино, `datetime` - время, в которое должна быть произведена запись'''
        try:
            self.deffered_tags.remove(str(datetime))
            schedule.clear(str(datetime))
            return True
        except: return False
        
    def write_format(self, data: Any):
        '''Отправляет данные в формате строки, полученной с помощью `format_send` на ардуино 
        и возвращает ответ от него, если соединение закрыто, то открывает его заново'''
        try:
            return self.communicate(self.format_send(data))
        except BaseException as error: 
            if self.logger:
                self.logger.exception(f"{error}; In ArduinoCommunicator.communicate() with input data: {data}")
            print(error)

    def write(self, data: str):# -> str | None:
        '''Отправляет данные в формате строки на ардуино и возвращает ответ от него, 
        если соединение закрыто, то открывает его заново'''
        try:
            if not self.connection.is_open:
                self.connection.open()
                print("write", data.encode())
            return self.connection.write(data.encode())
        except BaseException as error: 
            if self.logger:
                self.logger.exception(f"{error}; In ArduinoCommunicator.communicate() with input data: {data}")
            print(error)

    async def listener(self, timeout) -> None:
        '''Слушает порт, если в буффер не пуст и первый символ совпадает со `startflag`, то читает до `endflag` и отправляет 
        принятое сообщение в функцию `handler` (она вернет строку, то она будет отправлена как ответ).
        Если первый символ не совпадает, то буфер отчищается.'''
        while self.connection.is_open:
            await asyncio.sleep(timeout)
            #print(self.connection.port)  
            if self.connection.in_waiting > 0:
                start_symb = self.connection.read(1)
                #print("listener", start_symb.decode('utf-8'))

                if start_symb.decode('utf-8') == self.startflag:
                    response = self.connection.read_until(expected=self.endflag.encode())
                    print(self.connection.port, start_symb.decode('utf-8') + response.decode('utf-8'), start_symb + response)
                    response = self.handler(self.connection.port, start_symb + response, **dict())
                    #response = await self.handler(start_symb + response)
                    if response:
                        self.connection.write(response.encode())
                else: self.connection.reset_input_buffer()

    def close(self) -> None: 
        '''Закрывает соединение'''
        self.connection.close()

