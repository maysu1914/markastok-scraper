import pandas

from MarkaStokScraper import MarkaStokScraper


def get_first_column_from_excel(path):
    """
    get first column of excel by path of excel
    :param path:
    :return:
    """
    sheet = pandas.read_excel(path, header=None, usecols="A")
    data = pandas.DataFrame(sheet)
    values = [j.values[0] for i, j in data.iterrows()]
    return values


if __name__ == '__main__':
    links = get_first_column_from_excel("Software Developer Case Study URL's.xlsx")
    mss = MarkaStokScraper()
    mss.scrap(links)
