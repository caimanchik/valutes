from modules.csv_parser import CsvParser


def main():
    """
    Функция для запуска программы
    :return:
    """

    parser = CsvParser()
    parser.create_years_csv('src/vacancies_dif_currencies.csv', 'years')



if __name__ == '__main__':
    main()