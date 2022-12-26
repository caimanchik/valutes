import csv
import os
import time
import copy

import requests
import xml.etree.ElementTree as ET

from multiprocessing import Pool
from threading import Thread
from typing import Dict, List, Tuple
from queue import Queue
from modules.salary import Salary


def profile(func):
    """
    Функция для профилирования
    :param func: Функция
    :return: Результат выполнения функции
    """
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("Time: %.03f s" % (end - start))
        return result

    return wrapper


class CsvParser:
    """
    Класс для представления сущности парсера
    """
    def __init__(self, file_name: str):
        """
        Инициализация парсера
        """
        self.__year_data: Dict[str, List[List[str]]] = {}
        self.__title = []
        self.__currency_index: int = 0
        self.__count_currency: Dict[str, int] = {}

        self.__file_name = file_name

    def create_years_csv(self):
        """
        Метод создает csv файлы, разделенные по годам
        :return:
        """
        self.__parse_csv()
        self.__write_csv()

    def create_convert_csv(self):
        """
        Метод для создания csv файла с конвертацией валют
        :return:
        """
        window = self.__get_window()

        results = Queue()
        threads = []

        for year in range(int(window[0]), int(window[1]) + 1):
            for month in range(1, 13):
                th = Thread(target=get_converts_month, args=(year, str(month) if month >= 10 else f"0{month}", results))
                threads.append(th)
                th.start()

        for thread in threads:
            thread.join()

        headers = set([header for data in results.queue for header in data.keys()])
        headers.remove('date')

        headers = [e for e in headers if self.__count_currency.get(e, 0) > 5000]

        with open('convert.csv', 'w', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['date'] + headers)

            for e in sorted(results.queue, key=lambda x: x['date']):
                line = [e['date']] + [e[header] if header in e.keys() else '' for header in headers]
                writer.writerow(line)

    @staticmethod
    def handle_csv():
        """
        Функция для обработки csv файла и объединения колонки salary
        :return:
        """
        currencies = CsvParser.__get_currencies()

        if not os.path.isdir('converted'):
            os.mkdir('converted')

        files = os.listdir('years')

        args = map(lambda x: (x, copy.deepcopy(currencies)), files)

        mult_pool = Pool(len(files))

        mult_pool.starmap(handle_year_statistics, args)

    @staticmethod
    def __get_currencies() -> Dict[str, Dict[str, str | float]]:
        """
        Метод для получения словаря с ковертацией валют
        :return: Словарь с конвертацией валюь по месяцам
        """
        result: Dict[str, Dict[str, str | float]] = {}
        with open('convert.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            is_title = True
            title = []

            for row in reader:
                if is_title:
                    is_title = False
                    title = row
                    continue

                result[row[0]] = dict(zip(title[1:], [float(x) if x != '' else '' for x in row[1:]]))

        return result

    def __get_window(self) -> Tuple[int, int]:
        """
        Возвращает окно для запросов на сайт ЦБ РФ
        :return: Кортеж из начального и конечного годов
        """
        keys = list(sorted(self.__year_data.keys()))

        return int(keys[0]), int(keys[-1])

    def __parse_csv(self):
        """
        Метод для парсинга файла csv
        :return:
        """
        with open(self.__file_name, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=',')

            for row in reader:
                if len(self.__title) == 0:
                    self.__parse_title(row)
                    continue

                self.__parse_row(row)


    def __parse_title(self, title: List[str]):
        """
        Метод для парсинга заголовка csv файла
        :param title: Заголовок
        :return:
        """
        self.__title = title
        self.__currency_index = title.index('salary_currency')

    def __parse_row(self, row: List[str]):
        """
        Метод парсит вакансии и добавляет данные по годам в словарь self.__year_data
        :param row: Массив из строки файла
        :return:
        """

        if row[self.__currency_index] != '':
            self.__count_currency[row[self.__currency_index].upper()] = self.__count_currency.get(row[self.__currency_index].upper(), 0) + 1

        now_year = CsvParser.__get_year_from_row(row)

        year_vacancies = self.__year_data.get(now_year, [])
        year_vacancies.append(row)
        self.__year_data[now_year] = year_vacancies

    def __write_csv(self):
        """
        Метод записывает данные в отдельные csv файлы по годам в папке output_dir
        :return:
        """
        if not os.path.isdir('years'):
            os.mkdir('years')

        for key in self.__year_data.keys():
            with open(f"years/{key}.csv", 'w', encoding='utf-8-sig') as f:
                writer = csv.writer(f)

                writer.writerow(self.__title)
                writer.writerows(self.__year_data[key])

    @staticmethod
    def __get_year_from_row(row: List[str]) -> str:
        """
        Возвращает год вакансии из строки csv файла
        :param row: Массив из строки
        :return: Дата
        """
        return row[-1][0:4]


def get_converts_month(year: int, month: str, results: Queue):
    """
    Метод для получения словаря с конвертациями валют для указанных года и месяца
    :param year: Год
    :param month: Месяц
    :param results: Очередь, в которую добавить результат(сиспользуется для многопоточной реализации программы)
    :return:
    """
    url = f'http://www.cbr.ru/scripts/XML_daily.asp?date_req=01/{month}/{year}'
    response = requests.get(url)

    valcurs = ET.fromstring(response.content)

    convert_dict = {'date': f"{year}-{month}"}

    for valute in list(valcurs):
        nominal = 0
        value = 0
        name = ''

        for item in list(valute):
            if item.tag == 'Nominal': nominal = float(item.text.replace(',', '.'))
            if item.tag == 'Value': value = float(item.text.replace(',', '.'))
            if item.tag == 'CharCode': name = item.text

        convert_dict[name] = value / nominal

    results.put(convert_dict)


def handle_year_statistics(file_name: str, convert_dict: Dict[str, Dict[str, str | float]]):
    """
    Функция для обработки csv файла за определенный год

    :param file_name: Название чанка для обработки
    :param convert_dict: Словарь с конвертацией валют по годам
    :return:
    """
    with open(f'converted/{file_name}', 'w', encoding='utf-8-sig') as wr:
        writer = csv.writer(wr)
        with open(f"years/{file_name}", 'r', encoding='utf-8-sig') as r:
            reader = csv.reader(r, delimiter=',')
            is_title = True

            for row in reader:
                if is_title:
                    is_title = False
                    writer.writerow([row[0], 'salary'] + row[-2:])
                    continue

                salary = Salary(row[1], row[2], row[3])
                new_salary = salary.get_converted_salary(row[-1][:7], convert_dict)

                writer.writerow([row[0], new_salary] + row[-2:])
