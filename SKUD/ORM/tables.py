import json
from datetime import datetime
from dataclasses import dataclass

@dataclass
class VisitsHistory:
    port: str
    message: str
    pass_time: str = str(datetime.now().isoformat())
    
    def to_json(self):
        return json.dump(self.__dict__)

@dataclass
class RemoteSessions:
    address: str
    token: int
    event: str
    message: str
    sign_in_time: str = str(datetime.now().isoformat())
    
    def to_json(self):
        return json.dump(self.__dict__)

@dataclass
class History:
    action: str
    table: str
    type: str = None 
    values: str  = None
    date_time = str(datetime.now().isoformat())

@dataclass
class EntityView:
    card: int
    isSabotagedCard: bool
    cardAddDate: datetime
    right: int
    rightName: str
    rightAddDate: datetime
    rightDelDate: datetime     
    sid: int
    type: bool
    entityAddDate: datetime  
    entityDelDate: datetime  
     
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
                         sort_keys=True, indent=4)

@dataclass
class AccessRuleView:
    room: int
    roomName: str 
    roomAddDate: datetime  
    roomDeleDate: datetime  
    right: int
    rightName: str
    rightAddDate: datetime  
    rightDelDate: datetime  
    ruleAddDate: datetime  
    ruleDelDate: datetime  

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
                         sort_keys=True, indent=4)
