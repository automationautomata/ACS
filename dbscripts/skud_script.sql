-------------------------TABLES-------------------------

CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    number INTEGER NOT NULL,
    isSabotaged VARCHAR(1) NOT NULL,
    date_time_begin TEXT NOT NULL,
    date_time_end TEXT
);
-- 0 - не саботирована, 1 - саботирована 
CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    date_time_begin TEXT NOT NULL,
    date_time_end TEXT, 
    UNIQUE(name)
);
CREATE TABLE rights (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    date_time_begin TEXT NOT NULL,
    date_time_end TEXT
);
CREATE TABLE access_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    right INTEGER NOT NULL,
    room INTEGER NOT NULL,
    date_time_begin TEXT NOT NULL,
    date_time_end TEXT,
    FOREIGN KEY(room) REFERENCES rooms(id),
    FOREIGN KEY(right) REFERENCES rights(id),
    UNIQUE(right, room)
);
CREATE TABLE entities (
    card VARCHAR(4),
    sid INTEGER PRIMARY KEY NOT NULL,
    type VARCHAR(1) NOT NULL,
    right INTEGER NOT NULL,
    date_time_begin TEXT NOT NULL,
    date_time_end TEXT,
    FOREIGN KEY(card) REFERENCES cards(id),
    FOREIGN KEY(right) REFERENCES rights(id)
);

-------------------------VIEWES---------------------------

CREATE VIEW entities_view 
AS select card, 
          cards.number as cardsNumber,  
          cards.isSabotaged as isSabotagedCard,  
          cards.date_time_begin as cardAddDate, 
          cards.date_time_end as cardDelDate, 
          entities.right, 
          rights.name as rightName, 
          rights.date_time_begin as rightAddDate,
          rights.date_time_end as rightDelDate, 
          entities.sid,
          entities.type,
          entities.date_time_begin as entityAddDate,
          entities.date_time_end as entityDelDate
            from entities inner join cards on cards.id = entities.card    
                        inner join rights on entities.right = rights.id;

CREATE VIEW access_rules_view 
AS select access_rules.room, 
          rooms.name as roomName,  
          rooms.date_time_begin as roomAddDate, 
          rooms.date_time_begin as roomDelDate, 
          access_rules.right, 
          rights.name as rightName, 
          rights.date_time_begin as rightAddDate,
          rights.date_time_end as rightDelDate, 
          access_rules.date_time_begin as ruleAddDate,
          access_rules.date_time_end as ruleDelDate
            from access_rules inner join rooms on rooms.id = access_rules.room    
                        inner join rights on access_rules.right = rights.id;
--------------------------------------------------------------------------------    

INSERT into cards (number, isSabotaged, date_time_begin) values (12, 0, strftime('%Y-%m-%d %H:%M:%S', datetime('now'))), 
                                                                (15, 0, strftime('%Y-%m-%d %H:%M:%S', datetime('now')));             
INSERT into rooms (name, date_time_begin) values ('office', strftime('%Y-%m-%d %H:%M:%S', datetime('now'))), 
                                                 ('work'  , strftime('%Y-%m-%d %H:%M:%S', datetime('now'))),
                                                 ('UI'    , strftime('%Y-%m-%d %H:%M:%S', datetime('now')));
                                                                   
INSERT into rights (name, date_time_begin) values ('admin'   ,  strftime('%Y-%m-%d %H:%M:%S', datetime('now'))), 
                                                  ('employee',  strftime('%Y-%m-%d %H:%M:%S', datetime('now')));

INSERT into access_rules (right, room, date_time_begin) values (1, 1, strftime('%Y-%m-%d %H:%M:%S', datetime('now'))), 
                                                               (1, 2, strftime('%Y-%m-%d %H:%M:%S', datetime('now'))),
                                                               (1, 3, strftime('%Y-%m-%d %H:%M:%S', datetime('now'))),
                                                               (2, 2, strftime('%Y-%m-%d %H:%M:%S', datetime('now')));
                                                               
INSERT into entities (card, sid, type, right, date_time_begin) values (1, 1, 0, 1, strftime('%Y-%m-%d %H:%M:%S', datetime('now'))), 
                                                                      (2, 5, 0, 2, strftime('%Y-%m-%d %H:%M:%S', datetime('now')));
-- CREATE TRIGGER subotaged_card_not_in_entities
-- INSERT INSERT ON cards
-- BEGIN
--     SELECT RAISE(ABORT, 'CARD IN ENTITIES') 
--         WHERE SELECT card FROM entities INNER JOIN cards ON entities.card = cards.id
-- END;

-- -- Можно ли добавлять в таблицу записи с правом, которому в access_rules
-- -- сопоставлены все записи с заполненным полем date_time_end ????
-- CREATE TRIGGER entities_check_card_upd
-- BEFORE UPDATE OF card ON entities
-- BEGIN
--     SELECT RAISE(ABORT, 'CARD IS SABOTAGED') 
--         WHERE 0 < SELECT SUM(e.isSabotaged) 
--                         from new inner join cards 
--                             on new.card = cards.id AS e;
-- END;

-- CREATE TRIGGER entities_check_right_upd
-- BEFORE UPDATE OF right ON entities
-- BEGIN
--     SELECT RAISE(ABORT, 'RIGHT DATE ENDS DOES NOT CORRECT') 
--         WHERE NOT EXISTS(SELECT * from new inner join cards 
--                                 on new.right = rights.id 
--                                     WHERE rights.date_time_end = '');
-- END;

-- CREATE TRIGGER prevent_entities_insert_error
-- INSERT INSERT ON entities
-- BEGIN
--     SELECT RAISE(ABORT, 'CARD IS SABOTAGED') 
--         WHERE 0 < (SELECT SUM(e.isSabotaged) 
--                         from NEW inner join cards 
--                             on NEW.card = cards.id AS e) 

--     SELECT RAISE(ABORT, 'RIGHT DATE END DOES NOT CORRECT') 
--         WHERE NOT EXISTS(SELECT * from new inner join cards 
--                                 on NEW.right = rights.id 
--                                     WHERE rights.date_time_end = '');
-- END;

-- CREATE TRIGGER handle_delete_entities 
-- INSTEAD OF DELETE ON entities
-- BEGIN
--     UPDATE entities SET date_time_end=DATETIME('NOW')
--         WHERE id=NEW.id;
-- END;

-- CREATE TRIGGER handle_delete_access_rules 
-- INSTEAD OF DELETE ON access_rules
-- BEGIN
--     SELECT RAISE(ABORT, 'RIGHT WAS DELETED')
--         WHERE NOT EXISTS(SELECT * from new inner join rights 
--                                     on NEW.right = rights.id 
--                                         WHERE rights.date_time_end = '');

--     UPDATE access_rules SET date_time_end=DATETIME('NOW')
--         WHERE id=NEW.id;
-- END;

-- CREATE TRIGGER handle_delete_rights INSTEAD OF DELETE ON rights
-- BEGIN
--     UPDATE access_rules SET date_time_end=DATETIME('NOW')
--         WHERE right=NEW.id;

--     UPDATE rights SET date_time_end=DATETIME('NOW')
--         WHERE id=NEW.id AND date_time_end='';
-- END;

