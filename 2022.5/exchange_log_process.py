
from exchange_lib import *
import os
def readOriginFile(path='./origin_logs'):
    ls = set()
    for f in os.listdir(path): 
        f_name = os.path.join(path, f)
        if '_body' in f_name:
            with open(f_name, 'r') as ff:
                ls.add(ff.read())
    return list(ls)



# 处理ck和log的数据库，分别有两张表
class SQLProcess:

    def __init__(self, table_name, database_dict = {
                                                    'type': 'sqlite',
                                                    'name': "filtered_cks.db"
                                                   }, table_type='cookie', default_times=3):
        self.database_dict = database_dict
        self.table_name = self.getTableName(table_name)
        # # 默认为处理ck的表，如果需要处理logs，则table_type为'log'
        self.table_type = table_type
        if self.table_type == 'log':
            self.log_set = set()
        self.default_times = default_times
        print(self.table_name)
        self.createDatebase()
        self.createTable()
    
    def getTableName(self, name):
        if len(name) > 300:
            name = name[:300]
        if len(name) < 20:
            return name
        # temp = 'table_' + name.replace('=', '').replace('%', '').replace('_', '').split("key")[-1][::10]
        temp = 'table_' + name.replace('=', '').replace('%', '').replace('_', '').replace('.', '')[::10]
        return temp if len(temp) <= 20 else temp[:20]
    
    def deleteTable(self):
        self.c.execute(f'''
                        DROP TABLE IF EXISTS {self.table_name}
                        ''')
        self.conn.commit()
    
    def createDatebase(self):
        if 'type' not in self.database_dict:
            print("Error in database configure! Exit...")
            exit()
        
        if self.database_dict['type'] == 'mysql':
            try:
                start = time.time()
                self.conn = mysql.connect(
                    host = self.database_dict['host'],       # 数据库主机地址
                    port = self.database_dict['port'],
                    user = self.database_dict['user'],    # 数据库用户名
                    passwd = self.database_dict['passwd'],   # 数据库密码
                    database = self.database_dict['database']
                )
                end = time.time()
                # 3秒超时
                if end - start > 3:
                    raise Exception
                print("Connected to remote mysql successfully...")
            except Exception as e:
                print("Try to connecting to remote mysql but timeout occurs...", e)
                self.conn = sqlite.connect("filtered_cks.db")
                print("Connected to local sqlite successfully...")
        else:
            self.conn = sqlite.connect("filtered_cks.db")
            print("Connected to local sqlite successfully...")
        self.c = self.conn.cursor()
        return self.conn
        
    
    def createTable(self):
        if self.table_type == 'cookie':
            # 时间戳；ck；日期；优先级；权重（拟运行次数）
            self.c.execute(f'''CREATE TABLE IF NOT EXISTS {self.table_name}
                            (TIMESTAMP REAL PRIMARY KEY NOT NULL, 
                            USER_NAME TEXT NOT NULL, 
                            DATE TEXT NOT NULL, 
                            PRIORITY INT NOT NULL,
                            TIMES INT NOT NULL DEFAULT 0);
                            ''')
            self.conn.commit()
        elif self.table_type == 'log':
            self.c.execute(f'''CREATE TABLE IF NOT EXISTS {self.table_name}
                            (TIMESTAMP REAL PRIMARY KEY NOT NULL, 
                            LOG TEXT NOT NULL,
                            TIMES INT NOT NULL);
                            ''')
            self.conn.commit()

        else:
            print("ERROR in 'table_type'!")
            return

        print(f"Table {self.table_name} has been created.")

    def deleteTable(self):
        self.c.execute(f"DROP TABLE {self.table_name};")
        self.conn.commit()
        print(f"Table {self.table_name} has been deleted.")
    
    def insertLog(self, log, times=3):
        if self.table_type != 'log':
            return
        # 每次插入执行三次，存在即不插入
        p = self.c.execute(f'''
                        SELECT COUNT(*) from {self.table_name} WHERE LOG = '{log}'
                        ''')
        if self.c.fetchone()[0] > 0:
            print("ERROR IN INSERT LOG: LOG exists...")
            return
        else:
            # 插入times次数的log
            self.c.execute(f'''INSERT INTO {self.table_name} (TIMESTAMP, LOG, TIMES)
                                VALUES ({time.time()}, '{log}', {TIMES})''')
            
            # for i in range(times):
            #     self.c.execute(f'''INSERT INTO {self.table_name} (TIMESTAMP, LOG)
            #                     VALUES ({time.time()}, '{log}')''')
            self.conn.commit()
            print(f"Log has been inserted into Table {self.table_name}.")

    # 多层插入没有判断次数，存在就更新！！！
    def insertManyLog(self, logs, times=3):
        if self.table_type != 'log':
            return

        # 查询所有的log，存入set，去重
        self.c.execute(f'''
                    SELECT LOG from {self.table_name}
                    ''')
        for log in self.c.fetchall():
            self.log_set.add(log)

        dup_logs = []
        for log in logs:
            if log in self.log_set: 
                continue
            for t in range(times):
                dup_logs.append((time.time(), log, times))
                time.sleep(0.0001)
        # 存在则更新
        # self.c.executemany(f'''INSERT INTO {self.table_name} (TIMESTAMP, LOG, TIMES) VALUES (%s, %s, %s)
        #                     WHERE NOT EXISTS (SELECT * FROM {self.table_name} WHERE LOG=%s)
        #                     ''', dup_logs)
        # self.c.executemany(f"REPLACE INTO {self.table_name} (TIMESTAMP, LOG, TIMES) VALUES (%s, %s, %s)", dup_logs)
        self.c.executemany(f"INSERT INTO {self.table_name} (TIMESTAMP, LOG, TIMES) VALUES (%s, %s, %s)", dup_logs)
        self.conn.commit()
        print(f"Logs have been inserted into Table {self.table_name}. Inserted length : {len(dup_logs)}")

    def updateDualLog(self):
        pass


    # 取出一条log，并从中删除该条信息
    def getLog(self):
        if self.table_type != 'log':
            return
        # 查第一条select * from table  LIMIT 1
        p = self.c.execute(f'''
                        SELECT * from {self.table_name} LIMIT 1
                        ''')
        result = self.c.fetchone()
        # 将该条信息删除，或者次数-1DELETE FROM  WHERE
        if result is not None:
            if result[2] == 1:
                self.c.execute(f'''
                            DELETE FROM {self.table_name} WHERE LOG = {result[1]}
                            ''')
            else:
                self.c.execute(f"REPLACE INTO {self.table_name} (TIMESTAMP, LOG, TIMES) VALUES ({time.time()}, '{result[1]}', {result[2]-1})", )
            self.conn.commit()
            print(f"Log has been get and updated/deleted from Table {self.table_name}.")
            return result[1]
        else:
            print("ERROR IN GET LOG: No log in Table {self.table_name}. Please add log!")
            return ''
        return result[1] if result is not None else ''

    # 取出多条log，并从中删除
    def getManyLog(self, log_num=1, times=3):
        log_item_num = (log_num + times - 1) // times
        if self.table_type != 'log':
            return
        self.c.execute(f'''
                        SELECT * from {self.table_name} LIMIT {log_item_num}
                        ''')
        result = self.c.fetchall()
        if result is not None:
            self.c.execute(f'''
                        DELETE FROM {self.table_name} LIMIT {log_item_num}
                        ''')
            self.conn.commit()
            print(f"Logs (the first {log_item_num}) have been get and deleted from Table {self.table_name}.")
            res = []
            for x in list(result):
                for t in range(times):
                    res.append(x[1])
        else:
            print("ERROR IN GET LOG: No log in Table {self.table_name}. Please add log!")
            res = []
        res_length = len(res)
        for i in range(res_length, log_num):
            res.append('')
            print("ERROR IN GET LOG: Few logs in Table {self.table_name}. Please add log!")
        return res

    def insertItem(self, user_name, timestamp, year_month_day, priority):
        if self.findUserName(user_name, year_month_day):
            print(f"{getUserName(user_name)} is in Table {self.table_name}. Updating...")
            self.updateItem(user_name, timestamp, year_month_day, priority)
            return
        self.c.execute(f'''INSERT INTO {self.table_name} (USER_NAME, TIMESTAMP, DATE, PRIORITY)
                            VALUES ('{user_name}', {timestamp}, '{year_month_day}', {priority})''')
        self.conn.commit()
        print(f"Item {getUserName(user_name)} has been inserted into Table {self.table_name}.")

    def addTimes(self, user_name, year_month_day = str(datetime.date.today())):
        if not self.findUserName(user_name, year_month_day):
            print(f"Error in updating: No item found...")
            return
        self.c.execute(f'''
                        UPDATE {self.table_name} set 
                        TIMES = TIMES + 1
                        WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND DATE = '{year_month_day}'
                        ''')
        self.conn.commit()
        print(f"Item {getUserName(user_name)}'s times have been added in Table {self.table_name}.")
    
    def updateItem(self, user_name, timestamp, year_month_day, priority):
        if not self.findUserName(user_name, year_month_day):
            print(f"Error in updating: No item found...")
            return
        # 时间戳为primary key，不更新，ck动态更新，因为会失效
        # 优先级大于0时可以更新，但只更新权重
        if priority > 0:
            self.c.execute(f'''
                            UPDATE {self.table_name} SET 
                            USER_NAME='{user_name}',
                            DATE='{year_month_day}'
                            WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND PRIORITY > 0 AND DATE = '{year_month_day}'
                            ''')
            print(f"Item {getUserName(user_name)} has been updated for USER_NAME (with cookie). The weight is not updated.")
        else:
            # 小于或者等于0时全部更新
            self.c.execute(f'''
                            UPDATE {self.table_name} SET 
                            USER_NAME='{user_name}',
                            DATE='{year_month_day}',
                            PRIORITY={priority}
                            WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND PRIORITY > 0 AND DATE = '{year_month_day}'
                            ''')
            print(f"Item {getUserName(user_name)}:{priority} has been updated in Table {self.table_name}.")
        self.conn.commit()

    def updateItem_ALLCK(self, user_name, timestamp, year_month_day, priority):
        if not self.findUserName(user_name, year_month_day):
            print(f"Error in updating: No item found...")
            return

        # 只将数值更新为权重比较高的值和权重小于或等于0的值。
        self.c.execute(f'''
                        SELECT PRIORITY FROM {self.table_name} 
                        WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND PRIORITY > 0 AND DATE = '{year_month_day}'
                        ''')
        old_priority = int(self.c.fetchone()[0])
        # 更新权重条件：1. 当前权重大于0（未领到券且当前账号不火爆）；2. 在1的基础上，需要更新的权重小于等于0（抢到券或火爆）或权重大于旧权重（更新为更高的权重）
        if old_priority > 0 and (old_priority < priority or priority <= 0):
        # if self.c.fetchone()[0] < priority or priority <= 0:
            self.c.execute(f'''
                            UPDATE {self.table_name} SET 
                            USER_NAME='{user_name}',
                            DATE='{year_month_day}',
                            PRIORITY={priority}
                            WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND PRIORITY > 0 AND DATE = '{year_month_day}'
                            ''')
            print(f"Item {getUserName(user_name)}:{priority} has been updated in Table {self.table_name}.")
        else:
            # 权重更小，且权重大于0，则不更新权重，只更新数值。
            self.c.execute(f'''
                UPDATE {self.table_name} SET 
                USER_NAME='{user_name}',
                DATE='{year_month_day}'
                WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND PRIORITY > 0 AND DATE = '{year_month_day}'
                ''')
            print(f"Item {getUserName(user_name)} has been updated for USER_NAME (with cookie). The weight is not updated.")

        # # 时间戳为primary key，不更新，ck动态更新，因为会失效
        # # 优先级大于0时可以更新，但只更新ck
        # if priority > 0:
        #     self.c.execute(f'''
        #                     UPDATE {self.table_name} SET 
        #                     USER_NAME='{user_name}',
        #                     DATE='{year_month_day}'
        #                     WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND PRIORITY > 0 AND DATE = '{year_month_day}'
        #                     ''')

        #     print(f"Item {getUserName(user_name)} has been updated for USER_NAME (with cookie). The weight is not updated.")
        # else:
        #     # 小于或者等于0时全部更新
        #     self.c.execute(f'''
        #                     UPDATE {self.table_name} SET 
        #                     USER_NAME='{user_name}',
        #                     DATE='{year_month_day}',
        #                     PRIORITY={priority}
        #                     WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND PRIORITY > 0 AND DATE = '{year_month_day}'
        #                     ''')
        #     print(f"Item {getUserName(user_name)}:{priority} has been updated in Table {self.table_name}.")

        
        # self.c.execute(f'''
        #                 UPDATE {self.table_name} set 
        #                 DATE='{year_month_day}',
        #                 PRIORITY={priority}
        #                 WHERE USER_NAME='{user_name}' AND PRIORITY > 0 AND DATE = '{year_month_day}'
        #                 ''')
        #                 # UPDATE `table_3BA136F305ndD8D2eCF4C5AAE137` SET `USER_NAME` = 'pt_key=AAJiO0ZNADCcx_Fo6iKiAYKQQJA6D3swaJZSikd0kOGQ4R1Ka6qqkL0pYnpEs55BSOAzSbjNZWc;pt_pin=hxy287908634;' WHERE `USER_NAME` LIKE '%hxy%' and `DATE` = '2022-04-11'
        # self.c.execute(f'''
        #                 UPDATE {self.table_name} SET 
        #                 USER_NAME='{user_name}',
        #                 DATE='{year_month_day}',
        #                 PRIORITY={priority}
        #                 WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND PRIORITY > 0 AND DATE = '{year_month_day}'
        #                ''')
        self.conn.commit()
        # print(f"Item {getUserName(user_name)}:{priority} has been updated in Table {self.table_name}.")
    
    def filterUsers(self, user_number, year_month_day = str(datetime.date.today())):
        self.c.execute(f'''
                        SELECT USER_NAME, TIMES FROM {self.table_name} WHERE PRIORITY > -1 AND DATE = '{year_month_day}' ORDER BY PRIORITY DESC;
                        ''')
        p = self.c.fetchall()
        users, times = [], []
        for x in p:
            users.append(x[0])
            times.append(x[1])
        # users, times = [x[0] for x in p], [x[-1] for x in p]
        return users[:min(len(users), user_number)], times[:min(len(times), user_number)]
    
    def findUserName(self, user_name, year_month_day = str(datetime.date.today())):
        p = self.c.execute(f'''
                        SELECT count(*) from {self.table_name} WHERE USER_NAME LIKE '%{getUserName(user_name)}%' AND DATE = '{year_month_day}'
                        ''')
        return self.c.fetchone()[0] != 0
    
    def logsNumber(self):
        self.c.execute(f'''
                SELECT COUNT(*) from {self.table_name}
                ''')
        return self.c.fetchone()[0]
    def printAllLogs(self):
        self.printLogs(0x7fffffff)
        # if self.table_type != 'log': return
        # self.c.execute(f"SELECT * FROM {self.table_name}")
        # for item in self.c.fetchall():
        #     print(f"{item[1] if len(item[1]) < 30 else item[1][::50][:50]}")

    def printLogs(self, log_num=10):
        if self.table_type != 'log': return
        self.c.execute(f"SELECT * FROM {self.table_name} LIMIT {log_num}")
        for item in self.c.fetchall():
            print(f"{item[1] if len(item[1]) < 30 else item[1][::50][::-1][:50]}\t{item[2]}")

    def printTodayItems(self):
        self.printAllItems(str(datetime.date.today()))
    
    def printAllItems(self, year_month_day = None):
        if year_month_day is None:
            print(f"{'user_name'.ljust(17, ' ')}{'date'.ljust(12, ' ')}prio  times")
            self.c.execute(f"SELECT * FROM {self.table_name}")
            for item in self.c.fetchall():
                print(f"{getUserName(item[1]).ljust(17, ' ')}{item[2]}  {str(item[3]).ljust(6, ' ')}{item[4]}")
        else:
            print(f"{'user_name'.ljust(17, ' ')}{'date'.ljust(12, ' ')}prio  times")
            self.c.execute(f"SELECT * FROM {self.table_name} WHERE DATE = '{year_month_day}'")
            for item in self.c.fetchall():
                print(f"{getUserName(item[1]).ljust(17, ' ')}{item[2]}  {str(item[3]).ljust(6, ' ')}{item[4]}")
        
    def getAllUsers(self, year_month_day = str(datetime.date.today())):
        res = []
        for item in self.c.execute(f"SELECT USER_NAME from {self.table_name} WHERE DATE = '{year_month_day}'"):
            res.append(item[0])
        return res
            
    def close(self):
        self.conn.close()
    

database_dict = {
            "type":     'mysql',
            "host":     'xxxxxxx',        # 数据库主机地址
            "port":     'xxxx',
            "user":     'sql_coupon',        # 数据库用户名
            "passwd":   'xxxxx',      # 数据库密码
            "database": 'sql_coupon'
        }

log_sql = SQLProcess(table_name='speed_log', database_dict = database_dict, table_type='log')
log_sql.printLogs()
print(log_sql.logsNumber())
# log_sql.deleteTable()

# print(log_sql.logsNumber())
# for index, log in enumerate(logs):
#     print(f"processing {index+1}/{len(logs)}...")
#     log_sql.insertLog(log)

# for i in range(20):
#     print(log_sql.getManyLog(48))

# lp = LogProcess("./logs.npy")

# lp.remove()
# logs = readOriginFile()[9:]
# log_sql.insertManyLog(logs)
# for index, log in enumerate(logs):
#     print(f"processing {index+1}/{len(logs)}...")
#     log_sql.insertLog(log)
# # lp.save()
# log_sql.printLogs()