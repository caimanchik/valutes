import math
from typing import Dict


class Salary:
    """
    Класс для представления зарплаты
    """

    def __init__(
            self,
            salary_from: str | float,
            salary_to: str | float,
            salary_currency: str,
    ):
        """
        Инициализирует объект Salary
        Args:
            salary_from (str | float): Нижняя граница оклада
            salary_to (str | float): Верхняя граница оклада,
            salary_currency (str): Валюта оклада
        """
        self.__salary_from, self.__salary_to, self.__salary_currency = salary_from, salary_to, salary_currency

    def get_converted_salary(self, data: str, convert_dict: Dict[str, Dict[str, str | float]]) -> str | float:
        """
        Преобразует зарплату по условиям задачи 3.3.2
        """

        if self.__salary_currency == '' \
                or self.__salary_currency != 'RUR' and convert_dict[data].get(self.__salary_currency, '') == '' \
                or self.__salary_from == '' and self.__salary_to == '':
            return ''

        k = convert_dict[data][self.__salary_currency] if self.__salary_currency != 'RUR' else 1.0

        if self.__salary_from == '':
            if self.__salary_currency == 'RUR':
                return self.__salary_to
            return math.floor(float(self.__salary_to) * k)
        if self.__salary_to == '':
            if self.__salary_currency == 'RUR':
                return self.__salary_from
            return math.floor(float(self.__salary_from) * k)

        return Salary.__get_average_in_rubles(
            float(self.__salary_from),
            float(self.__salary_to),
            k)

    @staticmethod
    def __get_average_in_rubles(arg1: float, arg2: float, k: float) -> float:
        """
        Среднее значение в рублях
        :param arg1: Первое значение
        :param arg2: Второе значение
        :param k: Коэффициент перевода
        :return:
        """
        return math.floor(arg1 + arg2) / 2 * k
