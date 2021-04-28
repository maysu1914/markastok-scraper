import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

import requests as requests
from bs4 import BeautifulSoup


class MarkaStokScraper:
    base_url = "https://www.markastok.com"

    def __init__(self):
        self.executor = ThreadPoolExecutor()
        self.result = []

    def scrap(self, data):
        """
        Starter of scraping process
        :param data: list of links or a link
        :return: list of dicts scraped data
        """
        if type(data) is list:
            threads = [self.executor.submit(self.get_product_data, urljoin(self.base_url, url)) for url in data]
            for index, thread in enumerate(threads, start=1):
                # print(index)
                product_data = thread.result()
                if product_data:
                    self.result.append(product_data)
                else:
                    continue
        elif type(data) is str:
            product_data = self.get_product_data(urljoin(self.base_url, data))
            if product_data:
                self.result.append(product_data)
            else:
                pass
        return self.result

    def get_page_content(self, url, counter=3):
        """
        Content retriever
        :param url: the link whose content is to be returned
        :param counter: how many times of retrying
        :return: content of response
        """
        print(url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        }
        for count in range(1, counter + 1):
            try:
                response = requests.get(url, timeout=10, headers=headers)
                return response.content
            except Exception as e:
                print('Error occurred while getting page content!', count, url, e)
                continue
        return None

    def get_product_data(self, url):
        """
        Data scraper for product page
        :param url: product url
        :return: dict of data
        """
        page_content = self.get_page_content(url)
        data = {}
        #  check if page content retrieved successfully
        if page_content:
            soup = BeautifulSoup(page_content, "lxml")
            #  check if page has a 'Sepete Ekle' button
            if soup.select('.ad-to'):
                data['URL'] = url
                data['Product Code'] = self.get_product_code(soup.find('div', 'product-feature-content'))
                data['Product Name'] = self.get_product_name(soup.find('h1', 'product-name'))
                data['Availability'] = self.get_availability(soup.find('div', 'variantList'))
                data['Product Price'] = self.get_product_price(soup.find('span', 'currencyPrice discountedPrice'))
                data['Offer'] = self.get_offer(soup.find('div', 'detay-indirim'))
                data['Sale Price'] = self.get_product_price(soup.find('span', 'product-price'))
                # print(data)
                return data
            else:
                return data
        else:
            return data

    def get_product_code(self, element):
        """
        this site has some strange product code management system on product page
        :param element:
        :return: string
        """
        #  first digit always a number
        #  number or uppercase character until the . (dot)
        #  then number or uppercase character until the end
        #  (yes, some codes has uppercase character after the . (dot) )
        product_code_pattern = re.compile("^[0-9]{1}[A-Z0-9]+\.[A-Z0-9]+$")
        if element:
            #  get the last text, we know that the product code always at the end
            last_text = element.text.split()[-1]

            #  drop characters from left until the pattern is matched
            for digit_number in reversed(range(3, len(last_text) + 1)):
                text = last_text[-digit_number:]
                if product_code_pattern.fullmatch(text):
                    # print('accepted', text)
                    return text
                else:
                    continue

            #  if still no match
            return None
        else:
            return None

    def get_text(self, element):
        """
        it will parse the text of element without children's
        :param element:
        :return: string
        """
        return ''.join(element.find_all(text=True, recursive=False)).strip()

    def get_product_name(self, element):
        """
        it merge brand and product name
        :param element:
        :return: string product name
        """
        brand = element.span.text.strip()
        product = self.get_text(element)
        return ' '.join([brand, product])

    def get_availability(self, element):
        """
        calculate the availability of product
        :param element:
        :return: int
        """
        length = len(element.find_all("a", recursive=False))
        passives = len(element.select('.passive'))
        return "{:.2f}%".format((length - passives) / length * 100, 2).replace('.', ',')

    def get_product_price(self, element):
        """
        just a product price if exist
        :param element:
        :return: string
        """
        if element:
            return element.text.split()[0].strip()
        else:
            return None

    def get_offer(self, element):
        """
        just an offer if exist
        :param element:
        :return: string
        """
        if element:
            return element.text.replace('%', '').strip() + '%'
        else:
            return None
