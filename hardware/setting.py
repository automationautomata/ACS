import asyncio
import threading
import serial, serial.tools.list_ports
from typing import Callable
from threading import Thread
from hardware.arduino import ArduinoCommunicator


def getportsinfo() -> str:
    '''Возвращает информацию обо всех COM портах в json-подобном виде'''
    ports = list(serial.tools.list_ports.comports())
    getinfo = lambda port: '{'+f"\"Port\": \"{port.device}\",\
                                 \"Description\": \"{port.description}\", \
                                 \"Manufacturer\": \"{port.manufacturer}\""+'}'
    ports = ',\n'.join(getinfo(port) for port in ports)
    return '{'+f"{ports}"+'}'

def create_listeners_thread(arduinos: list[ArduinoCommunicator], 
                            start_sleep_time: int = 0,  delta: int = 0.001, isdaemon: bool = True) -> Thread:
    '''Создает поток, асинхронно выполняющий прослушивание портов, `arduinos` - подключенные устройства,
    `start_sleep_time` - время сна первой функции, `delta` - дельта между временем сна двух функций,
    `isdaemon` - подчиненный ли поток по отнощению к главному.'''
    async def ini():
        tasks = [asyncio.create_task(ard.listener(start_sleep_time + ind*delta)) for ind, ard in enumerate(arduinos)]
        await asyncio.gather(*tasks)
        print(f"Service {threading.get_native_id()} restarted.")

    thread = Thread(target=lambda:asyncio.run(ini()), daemon=False)
    print("ard thread", thread.daemon)
    return thread

def arduions_configuring(ports: list[str], 
                        handler: Callable[[bytes], str], isdaemon=True, handler_kwargs=None) -> tuple[Thread, dict[str, ArduinoCommunicator]]: 
    '''Настройка группы адруино, подключенных к портам из `ports` и с обработчиком входных данных `handler`,
    `handler_kwargs` - его аргументы'''
    arduinos = {}
    for port in ports:
        arduinos[port] = ArduinoCommunicator(port=port, handler=handler, handler_kwargs=handler_kwargs)
    thread = create_listeners_thread(list(arduinos.values()), isdaemon=isdaemon)
    return thread, arduinos
