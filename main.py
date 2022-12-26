from modules.csv_parser import CsvParser


def main():
    """
    Функция для запуска программы
    :return:
    """

    parser = CsvParser('src/vacancies_dif_currencies.csv')

    parser.create_years_csv()
    parser.create_convert_csv()
    CsvParser.handle_csv()


if __name__ == '__main__':
    main()