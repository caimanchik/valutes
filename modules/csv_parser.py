import csv
import os
import time
from typing import Dict, List


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
    def __init__(self):
        """
        Инициализация парсера
        """
        self.__year_data: Dict[str, List[List[str]]] = {}
        self.__title = []
        self.__currency_index: int = 0
        self.__count_currency: Dict[str, int] = {}
        self.__window = []

    def create_years_csv(self, file_name: str, output_dir: str):
        """
        Метод создает csv файлы, разделенные по годам
        :param file_name: Название файла для парсинга
        :param output_dir: Название директории для чанков
        :return:
        """
        self.__parse_csv(file_name)
        self.__write_csv(output_dir)

    def __parse_csv(self, file_name: str):
        """
        Метод для парсинга файла
        :param file_name: Название файла для парсинга
        :return:
        """
        with open(file_name, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=',')

            for row in reader:
                if len(self.__title) == 0:
                    self.__parse_title(row)
                    continue

                self.__parse_row(row)


    def __parse_title(self, title: List[str]):
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

    def __write_csv(self, output_dir: str):
        """
        Метод записывает данные в отдельные csv файлы по годам в папке output_dir
        :param output_dir: Название директории для чанков
        :return:
        """
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        for key in self.__year_data.keys():
            with open(f"{output_dir}/{key}.csv", 'w', encoding='utf-8-sig') as f:
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