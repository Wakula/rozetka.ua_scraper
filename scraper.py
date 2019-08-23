from bs4 import BeautifulSoup
import requests
import csv
from selenium import webdriver


def get_html_soup(url):
    source = requests.get(url)
    soup = BeautifulSoup(source.text, 'lxml')
    return soup


def get_total_pages(soup):
    nav_bar = soup.find('nav', id='navigation_block')
    items = nav_bar.find_all('li')
    last_item = items[-1]
    total_pages = int(last_item['id'].replace('page', ''))
    return total_pages


def remove_all(text, *args):
    for i in args:
        text = text.replace(i, '')
    return text.strip()


def parse_title(item):
    title_div = item.find('div', class_='g-i-tile-i-title clearfix')
    text = title_div.a.text
    text = text.split('+')[0]
    return remove_all(text, 'Суперцена', 'Ноутбук', '!!!')


def parse_price(item):
    price_block = item.find('div', class_='inline')
    div_old_price = price_block.find('div', class_='g-price-old-uah')

    if div_old_price is not None:
        old_price = str(div_old_price.contents[0])
        old_price = old_price.replace(' ', '')
    else:
        old_price = None
    div_current_price = price_block.find('div', class_='g-price-uah')
    current_price = str(div_current_price.contents[0])
    current_price = current_price.replace(' ', '')
    return old_price, current_price


def parse_out_of_stock(item):
    unavailable = item.find('div', class_='g-i-status out_of_stock')
    return 'out of stock' if unavailable else None


def main():
    try:
        url = 'https://rozetka.com.ua/notebooks/c80004/filter/'
        soup = get_html_soup(url)
        driver = webdriver.Chrome()
        csv_file = open('data.csv', 'w')
        data_writer = csv.writer(csv_file)
        total_pages = get_total_pages(soup)

        for page_id in range(1, total_pages+1):
            page_url = f'{url}page={page_id}'
            driver.get(page_url)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            items = soup.find_all('div', class_='g-i-tile g-i-tile-catalog')

            for item in items:
                if item.find('div', class_='g-i-status unavailable') is  not None:
                    driver.close()
                    csv_file.close()
                    return
                title = parse_title(item)
                old_price, current_price = parse_price(item)
                out_of_stock = parse_out_of_stock(item)
                row = (title, current_price, old_price, out_of_stock)
                data_writer.writerow(row)
    finally:
        driver.close()
        csv_file.close()


if __name__ == '__main__':
    main()
