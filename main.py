import pandas
import pygsheets
from pygsheets import SpreadsheetNotFound

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


def upload_dict_to_google_sheet(data, filename):
    #  Read before continue: https://pygsheets.readthedocs.io/en/latest/authorization.html
    gc = pygsheets.authorize(client_secret='client_secret.json')
    df = pandas.DataFrame()

    #  declaring titles of sheets
    for key, value in data[0].items():
        df[key] = []

    for product in data:
        df = df.append(product, ignore_index=True)

    #  access spread sheet
    try:
        sh = gc.open(filename)
    except SpreadsheetNotFound:
        #  create if not exist
        gc.sheet.create(filename)
        sh = gc.open(filename)

    #  select the first sheet
    wks = sh[0]

    #  make the headers bold
    for cell in ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1']:
        header = wks.cell(cell)
        header.text_format['bold'] = True
        header.update()

    #  update the first sheet with df, starting at cell B2.
    wks.set_dataframe(df, (0, 0))


if __name__ == '__main__':
    links = get_first_column_from_excel("Software Developer Case Study URL's.xlsx")
    mss = MarkaStokScraper()
    data = mss.scrap(links)
    upload_dict_to_google_sheet(data, "Markastok | Ürün Raporu")
