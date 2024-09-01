import json
from threading import Thread
from typing import Any, Callable
import tornado
from tornado.websocket import WebSocketHandler

from remote.tools import Actions, Answer, WebsoketClients


class AuthenticationHandler(tornado.web.RequestHandler):
    '''Класс для аутентификации'''
    def initialize(self, authenticatior: Callable[[str], Answer]):
        self.authenticatior = authenticatior

    def get(self) -> None:
        answer = self.authenticatior(self.get_body_argument("auth"))
        self.write(answer.toJSON())


class Websoket(WebSocketHandler):
    def initialize(self, action: Actions) -> None:
        self.actions = action.actions_map()
        self.verify = action.verify
        self.clients = WebsoketClients()
    
    def open(self):
        self.id = self.clients.add(self)
        print("WebSocket opened")

    def on_message(self, data):
        msg = json.loads(data)
        if self.veryfy(msg["token"]):
            self.actions[msg["action"]]
        self.write_message(f"You said: {data}")

    def on_close(self):
        self.clients.remove(self.id)
        print("WebSocket closed")

#type Router = list[tuple[str, Any] | tuple[str, Any, dict]]

def create_tornado_server(port: int, 
                          router, #: Router,  
                          auth: Callable[[str], Answer],
                          ws_actions: Any = None,
                          isdaemon: bool = True) -> tuple[Thread, tornado.web.Application]:
    '''Создает поток, обрабатывыающий запросы от десктоп приложений.
    `port` - номер сокета, 
    `router` - список из обработчиков сообщений от клиента по HTTP,
    `ws` - обрабатывает сообщения по websocket,
    `auth` - функция, производящяя аутентификацию, 
    `isdaemon` - подчиненный ли поток по отношению к главному.'''
    handlers = router + [(r"/auth", AuthenticationHandler, dict(authenticatior=auth))]
    if ws_actions: 
        handlers.append((r"/wss", Websoket, dict(actions=ws_actions)))
    

    app = tornado.web.Application(handlers)
    
    app.listen(port)
    return Thread(target=tornado.ioloop.IOLoop.current().start, daemon=isdaemon), app
