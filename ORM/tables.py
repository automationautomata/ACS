import json
from datetime import datetime

class VisitsHistory:
    def __init__(self, port: str, message: str):
        self.port = port
        self.message = message
        self.pass_time = str(datetime.now().isoformat())
    def toJSON(self):
        return json.dump(self.__dict__)
    
class RemoteSessions:
    def __init__(self, address: str, token: int, event: str, message: str):
        self.address = address
        self.token = token
        self.event = event
        self.message = message
        self.sign_in_time = str(datetime.now().isoformat())
    def toJSON(self):
        return json.dump(self.__dict__)

class History():
    def __init__(self, action: str, table: str, 
                       type: str = None, values: str  = None) -> None:
        self.action = action
        self.table = table
        self.type = type
        self.values = values
        self.date_time = datetime.now().isoformat()

class EntityView:
     def __init__(self, **kwargs) -> None:
        self.card = kwargs["card"]
        self.isSabotagedCard = kwargs["isSabotagedCard"]
        self.cardAddDate = kwargs["cardAddDate"]
        self.right = kwargs["right"]
        self.rightName = kwargs["rightName"]
        self.rightAddDate = kwargs["rightAddDate"]
        self.rightDelDate = kwargs["rightDelDate"]
        self.sid = kwargs["sid"]
        self.type = kwargs["type"]
        self.entityAddDate = kwargs["entityAddDate"]
        self.entityDelDate = kwargs["entityDelDate"]
     def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
                         sort_keys=True, indent=4)
     
class AccessRuleView:
     def __init__(self, room, roomName, roomAddDate, roomDeleDate,
                        right, rightName, rightAddDate, rightDelDate, 
                        ruleAddDate, ruleDelDate):
        self.room = room 
        self.roomName = roomName  
        self.roomAddDate = roomAddDate
        self.roomDeleDate = roomDeleDate 
        self.right = right
        self.rightName = rightName
        self.rightAddDate = rightAddDate
        self.rightDelDate = rightDelDate
        self.ruleAddDate = ruleAddDate
        self.ruleDelDate = ruleDelDate
     def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
                         sort_keys=True, indent=4)
