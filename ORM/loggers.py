from ORM.database import DatabaseConnection
from ORM.tables import RemoteSessions, VisitsHistory

class VisitLogger(DatabaseConnection):
    '''Класс для установки соединения с БД посещений'''

    def addvisit(self, row: VisitsHistory):
        '''Добавляет запись в таблицу истории посещений комнат. `row` - добавляемая строка'''
        conn = self.threadsafe_connect()
        cursor = conn.cursor()
        sql = "INSERT INTO visits_history (port, message, pass_time) VALUES (?,?,?);"
        data = (row.port, row.message, row.pass_time)
        try: 
            cursor.execute(sql, data)
            conn.commit()
            return True
        except BaseException as error: 
            print("ERR", error)
            return False
        
    def addsession(self, row: RemoteSessions):
        conn = self.threadsafe_connect()
        cursor = conn.cursor()
        sql = "INSERT INTO remote_sessions (address, token, event, message, sign_in_time) VALUES (?,?,?);"
        data = (row.address, row.token, row.event, row.message, row.sign_in_time)
        try: 
            cursor.execute(sql, data)
            conn.commit()
            return True
        except BaseException as error: 
            print("ERR", error)
            return False