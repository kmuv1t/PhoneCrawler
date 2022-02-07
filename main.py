import os
import re
import threading

import requests
from bs4 import BeautifulSoup

URL = os.environ.get('TARGET_URL')
THREADS = list()
LINKS = list()


def request(url):
    try:
        ans = requests.get(url)  # URL Request
        if ans.status_code == 200:
            return ans.text
        else:
            print('Error, unable to complete request.')
    except Exception as err:
        print(f'Error, {err}.')


def parsing(html_ans):
    try:
        soup = BeautifulSoup(html_ans, 'html.parser')  # Parsing
        return soup
    except Exception as err:
        print(f'Error, {err}.')


def find_urls(soup):
    try:
        for link in soup.find_all('a', class_='card'):  # Route Crawler
            LINKS.append(link['href'])
    except:
        print('Unable to append links.')


def find_phone():
    while True:
        try:
            link = LINKS.pop(0)
        except:
            return None
        ans = request(URL+link)
        if ans:
            sp = parsing(ans)
            text = sp.find_all('div', class_='sixteen wide column')[2].p.get_text().strip()
            regex = re.findall(r"\(?0?([1-9]{2})[ \-\.\)]{0,2}(9?[ \-\.]?\d{4})[ \-\.]?(\d{4})", text)  # Telephone Regex
            if regex:
                for phones in regex:
                    print(f"Found ({(phones[0])}) {phones[1]}-{phones[2]} in route {link}")
                    export_phones(f'({(phones[0])}) {phones[1]}-{phones[2]}')


def multi_thread(task):
    for i in range(10):  # Number of desired Threads
        t = threading.Thread(target=task)
        THREADS.append(t)

    for t in THREADS:
        t.start()

    for t in THREADS:
        t.join()


def phone_crawler(website):
    ans = request(website)
    if ans:
        soup = parsing(ans)
        find_urls(soup)
        multi_thread(find_phone)  # Phone Crawler


def export_phones(phones):
    try:
        with open('phone_dump.csv', 'a') as file:  # Export numbers
            file.write(f'{phones}\n')
    except Exception as err:
        print(f'Error, {err}.')


if __name__ == '__main__':
    phone_crawler(URL+'/automoveis')  # Target URL
