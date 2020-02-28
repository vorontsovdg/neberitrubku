import requests
from bs4 import BeautifulSoup
import re
import csv
from multiprocessing import Pool
import argparse

url= 'https://www.neberitrubku.ru/search?q='
field_names = ['phone', 'overall', 'rating', 'categories']

def preprocess(phone):
    try:
        phone = '+7' + ''.join([number for number in phone if number.isdigit()])[-10:]
        return phone
    except IndexError as e:
        return phone

def find_overall(html):
    soup = BeautifulSoup(html, 'html.parser')
    try:
        overall = ' '.join(re.findall(r'\w+', soup.find(class_ = 'number').text.lower()))
    except AttributeError as e:
        overall = ''
    return overall

def find_rating(html):
    soup = BeautifulSoup(html, 'html.parser')
    try:
        rating = ' '.join(soup.find(class_ = 'description').find(class_ = 'ratings').text.splitlines())
    except AttributeError as e:
        rating = ''
    return rating

def find_categories(html):
    soup = BeautifulSoup(html, 'html.parser')
    try:
        categories = [line.text for line in soup.find(class_ = 'categories').find_all('li')]
    except AttributeError as e:
        categories = ''
    return categories


def main(phone):
    text = requests.get(url + phone, allow_redirects = True).text
    overall = find_overall(text)
    rating = find_rating(text)
    categories = find_categories(text)
    with open('./results.csv', 'a') as f:
        csvWriter = csv.DictWriter(f, fieldnames = field_names)
        csvWriter.writerow({'phone':phone,
                            'overall':overall,
                            'rating':rating,
                            'categories':categories})


def parse():
    parser = argparse.ArgumentParser(description="""Script downloads user reviews about phone numbers from site http://neberitrubku.ru and stores them in file results.csv""")
    parser.add_argument('-f', type = str, help='Source file with phone numbers')
    parser.add_argument('--threads', type = int, default=4, help='Number of threads to request page\nDefault value = 4')
    args = parser.parse_args()
    return args
  
if __name__ == '__main__':
    args = parse()
    with open(args.f, 'r') as f:
        phones = [preprocess(phone) for phone in f.readlines()]
    with Pool(args.threads) as p:
        p.map(main, phones)
