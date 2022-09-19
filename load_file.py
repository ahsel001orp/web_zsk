import dataBase
from xml.etree import ElementTree as ET
from subprocess import Popen, PIPE, CREATE_NO_WINDOW
from xlsxwriter import Workbook
from datetime import datetime
from os import remove

def write_descript(worksheet, i, j):
    worksheet.write(i, j, 'Номер клиента')
    worksheet.write(i, j + 1, 'ИНН клиента')
    worksheet.write(i, j + 2, 'Тип клиента')
    worksheet.write(i, j + 3, 'Краткое нименование')
    worksheet.write(i, j + 4, 'Уровень риска')
    worksheet.write(i, j + 5, 'CMAINRISK')
    worksheet.write(i, j + 6, 'CADDRISK1')
    worksheet.write(i, j + 7, 'CADDRISK2')
    worksheet.write(i, j + 8, 'CADDRISK3')
    worksheet.write(i, j + 9, 'Дата обновления в ЦБ')

def load(fl):
    try:
        old_clients = dataBase.get_our_risk_client()
        ns = {'version': 'test'}
        tree = ET.parse(fl)
        root = tree.getroot()
        name = str(root.tag)
        start = name.find('{')
        end = name.find('}')
        ns['version'] = name[start + 1:end]
        print("Очищаем таблицу...")
        dataBase.clear_risk()
        nvl = lambda foo, bar: bar if foo is None else foo
        count = 0
        print("Парсим XML...")
        with open("result.csv", 'w', encoding='windows-1251') as file:
            for row in root.findall("version:RISK", ns):
                client = []
                client.append(str(nvl(row.find("version:inn", ns), root).text).replace("\n  ", ""))
                client.append(str(nvl(row.find("version:client_type", ns), root).text).replace("\n  ", ""))
                client.append(str(nvl(row.find("version:risk_level", ns), root).text).replace("\n  ", ""))
                client.append(str(nvl(row.find("version:MainRisk", ns), root).text).replace("\n  ", ""))
                client.append(str(nvl(row.find("version:AddRisk1", ns), root).text).replace("\n  ", ""))
                client.append(str(nvl(row.find("version:AddRisk2", ns), root).text).replace("\n  ", ""))
                client.append(str(nvl(row.find("version:AddRisk3", ns), root).text).replace("\n  ", ""))
                client.append(str(nvl(row.find("version:risk_date", ns), root).text).replace("\n  ", ""))
                file.write(';'.join(str(elem) for elem in client))
                file.write('\n')
                count += 1
        print("Пишем в базу...")
        #dataBase.set_env()
        with Popen('load.bat', stdout=PIPE, stderr=PIPE, creationflags=CREATE_NO_WINDOW) as proc:
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
        new_clients = dataBase.get_our_risk_client()
        print("Формируем отчет...")
        workbook = Workbook('M:\\ЗСК\\Отчеты\\test_Our_client_in_risk_%s.xlsx'
                                       % datetime.now().strftime('%d-%m-%Y'))
        worksheet = workbook.add_worksheet()
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 80)
        worksheet.set_column('J:J', 15)
        worksheet.set_column('K:K', 20)
        i, j = 0, 0
        new_block = list(set(new_clients) - set(old_clients))
        if len(new_block) > 0:
            worksheet.write(i, j, 'Клиенты из нового файла, претерпевшие изменения')
            i += 1
            write_descript(worksheet, i, j)
            i += 1
            for data_arr in new_block:
                for data in data_arr:
                    worksheet.write(i, j, str(data))
                    j += 1
                i += 1
                j = 0
            i += 1
            j = 0
        del_block = list(set(old_clients) - set(new_clients))
        if len(del_block) > 0:
            worksheet.write(i, j, 'Клиенты из старого файла, претерпевшие изменения')
            i += 1
            write_descript(worksheet, i, j)
            i += 1
            for data_arr in del_block:
                for data in data_arr:
                    worksheet.write(i, j, str(data))
                    j += 1
                i += 1
                j = 0
            i += 1
            j = 0
        if i == 0:
            worksheet.write(i, j, 'Изменений не обнаружено')
            i += 1
            worksheet.write(i, j, 'Совпавшие клиенты')
            i += 1
            write_descript(worksheet, i, j)
            i += 1
            for data_arr in new_clients:
                for data in data_arr:
                    worksheet.write(i, j, str(data))
                    j += 1
                i += 1
                j = 0
            i += 1
            j = 0
        else:
            worksheet.write(i, j, 'Клиенты из прежней загрузки')
            i += 1
            write_descript(worksheet, i, j)
            i += 1
            for data_arr in old_clients:
                for data in data_arr:
                    worksheet.write(i, j, str(data))
                    j += 1
                i += 1
                j = 0
            i += 1
            j = 0
            worksheet.write(i, j, 'Клиенты из новой загрузки')
            i += 1
            write_descript(worksheet, i, j)
            i += 1
            for data_arr in new_clients:
                for data in data_arr:
                    worksheet.write(i, j, str(data))
                    j += 1
                i += 1
                j = 0
            i += 1
            j = 0
        workbook.close()
        print("Успех!!!")
    except Exception as e:
        print(e)