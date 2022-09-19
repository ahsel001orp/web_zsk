import cx_Oracle
from os import environ
from tkinter import messagebox as mb

def connect():
    environ["ORACLE_HOME"] = r'T:\Oracl11clt\product\11.2.0\client_1'
    environ["PATH"] = r"T:\Oracl11clt\product\11.2.0\client_1\BIN;" + environ["PATH"]
    ip = environ.get('ip_db').split(':')
    dsn_tns = cx_Oracle.makedsn(ip[0], ip[1], service_name='test')
    return cx_Oracle.connect(user=environ.get('login_db'), password=environ.get('password_db'), dsn=dsn_tns)

def clear_risk():
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute('delete from zsk_risk')
        conn.commit()
    except Exception as e:
        mb.showerror('Ошибка', f"При очистке таблица zsk_risk произошла ошибка: {str(e)}")

def get_150_tabel(q):
    companies = []
    conn = connect()
    cursor = conn.cursor()
    for row in cursor.execute(f"select * from zsk_risk where 1=1 "
                              f"and CINN like \'{q}%\' "
                              f"order by IRISK_LEVEL desc "
                              f"FETCH NEXT 150 ROWS ONLY"):
        map_list = {"INN": row[0],
                    "Type": row[1],
                    "Risk_level": row[2],
                    "Code0": row[3],
                    "Code1": row[4],
                    "Code2": row[5],
                    "Code3": row[6],
                    "Date": row[7].strftime("%d.%m.%y")}
        companies.append(map_list)
    return companies

def inser_risk(client):
    try:
        conn = connect()
        cursor = conn.cursor()
        write = f"INSERT INTO zsk_risk\n" \
                f"(CINN, CCLIENT_TYPE, IRISK_LEVEL, CMAINRISK, CADDRISK1, CADDRISK2, CADDRISK3, DRISK_DATE)\n" \
                f"VALUES\n" \
                f"(\'{client[0]}\', \'{client[1]}\', \'{client[2]}\', \'{client[3]}\', \'{client[4]}\', \'{client[5]}\', \'{client[6]}\', to_date(\'{client[7]}\', \'yyyy-mm-dd\'))"
        print(write)
        cursor.execute(f"INSERT INTO zsk_risk\n" 
                       f"(CINN, CCLIENT_TYPE, IRISK_LEVEL, CMAINRISK, CADDRISK1, CADDRISK2, CADDRISK3, DRISK_DATE)\n" 
                       f"VALUES\n"
                       f"(\'{client[0]}\', \'{client[1]}\', \'{client[2]}\', \'{client[3]}\', \'{client[4]}\', \'{client[5]}\', \'{client[6]}\', to_date(\'{client[7]}\', \'yyyy-mm-dd\'))")
        conn.commit()
    except Exception as e:
        mb.showerror('Ошибка', f"При записе строки {client}, произошла ошибка: {str(e)}")

def get_data():
    result = []
    conn = connect()
    cursor = conn.cursor()
    for row in cursor.execute(f'select case when CCUSFLAG = 2 then 0\n'
                              f'when CCUSFLAG = 4 then 1 end,\n'
                              f'case when LENGTH(CCUSNAME) <255 then CCUSNAME\n'
                              f'else CCUSNAME_SH end, CCUSNUMNAL\n'
                              f'from cus where CCUSFLAG in (2,4)\n'
                              f'and ICUSSTATUS in (2,0)\n'
                              f'and ICUSNUM in (select IACCCUS from acc\n'
                              f'where CACCPRIZN in (\'О\', \'Б\')\n'
                              f'and CACCACC in (select distinct CGACACC from gac where IGACCAT = 3\n'
                              f'and IGACNUM in (1,2,24,36,39,40,41,124,131,162)))\n'
                              f'and nvl(CCUSOKVED2, \'0\') not like \'%84.11%\' \n'
                              f'and nvl(CCUSOKVED, \'0\') not like \'%84.11%\'\n'
                              f'order by CCUSFLAG, ICUSNUM'):
        result.append(row)
    return result

def get_our_risk_client():
    result = []
    conn = connect()
    cursor = conn.cursor()
    for row in cursor.execute(f'select c.ICUSNUM, z.CINN,\n'
                              f'case when c.CCUSFLAG = 2 then \'Юридическое лицо\'\n'
                              f'when c.CCUSFLAG  =4 then \'Индивидуальный предприниматель\'\n'
                              f'else c.CCUSFLAG end,\n'
                              f'c.CCUSNAME_SH, z.IRISK_LEVEL,\n'
                              f'nvl(CMAINRISK, \'НЕТ\'), nvl(CADDRISK1, \'НЕТ\'), nvl(CADDRISK2, \'НЕТ\'),\n'
                              f' nvl(CADDRISK3, \'НЕТ\'), TO_CHAR(DRISK_DATE, \'DD.MM.YYYY\'),\n'
                              f'case when EXISTS  (select 1 from acc where IACCCUS = c.ICUSNUM and CACCPRIZN <> \'З\')\n'
                              f'then \'Есть открытые счета\' else \'Нет открытых счетов\' end\n'
                              f'from cus c, zsk_risk z where c.CCUSFLAG in (2, 4)\n'
                              f'and c.CCUSNUMNAL = z.CINN ORDER BY c.ICUSNUM'):
        result.append(row)
    return result

def get_client(id):
    result = []
    conn = connect()
    cursor = conn.cursor()
    for row in cursor.execute(f'select case when CCUSFLAG = 2 then 0\n'
                              f'when CCUSFLAG = 4 then 1 end,\n'
                              f'case when LENGTH(CCUSNAME) <255 then CCUSNAME\n'
                              f'else CCUSNAME_SH end, CCUSNUMNAL, CCUSKSIVA\n'
                              f'from cus where ICUSNUM = {id}\n'):
        result.append(row)
    return result