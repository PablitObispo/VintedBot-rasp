from typing import Set, List
import os
import csv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

class NotifierVinted:
    def __init__(self, filename: str, url, channel):
        self.filename = filename
        self.fieldnames = ["user", "price", "size", "name", "brand", "link", "image", "id"]
        self.url = url
        self.searching_items = False
        self.channel = channel

    #crée le fichier csv (de backup) s'il n'existe pas 
    def create_csv_file(self) -> None:
        if not os.path.exists(self.filename):
            with open(self.filename, mode="w", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self.fieldnames)
            print(f'création fichier de backup {self.filename}')

    def run_driver(self):
        #configure le driver en headless
        user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36"

        options = webdriver.ChromeOptions()
        options.headless = True
        options.binary_location = "/usr/bin/chromium-browser"
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--start-maximized")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')

        service = Service(executable_path="./chromedriver")
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.get(self.url)

    #récupère les ids des articles déjà présents dans le fichier csv
    def get_all_ids(self) -> Set:
        ids = set()
        with open(self.filename, mode="r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=self.fieldnames)
            for row in reader:
                ids.add(row['id'])
        return ids

    def get_new_items(self):
        # récupère les articles sur le site
        article_body = self.driver.find_element(By.CLASS_NAME, "feed-grid")
        current_articles = article_body.find_elements(By.CSS_SELECTOR, ".feed-grid__item:not(.feed-grid__item--full-row)")

        list_of_items = []
        new_items = []

        #ajoute les articles en dict dans list_of_items
        for article in current_articles:
            try:
                user, price, likes, size, brand = [elem.text for elem in article.find_elements(By.CLASS_NAME, "Text_text__QBn4-")]
                link = article.find_element(By.CSS_SELECTOR, "a.ItemBox_overlay__1kNfX").get_attribute('href')
                image = article.find_element(By.CSS_SELECTOR, ".ItemBox_image__3BPYe img").get_attribute('src')

                item = dict()

                del likes
                user = user.strip()
                price = price.strip()
                size = size.strip()
                brand = brand.strip()
                link = link.strip()
                image = image.strip()
                name = " ".join(link.split("/")[-1].split("-")[1:]).title()
                id_ = link.split('/')[-1].split('-')[0]

                item['user'] = user
                item['price'] = price
                item['size'] = size
                item['name'] = name
                item['brand'] = brand
                item['link'] = link
                item['image'] = image
                item['id'] = id_

                list_of_items.append(item)

            except ValueError:
                pass

        #stock les articles dans un fichier csv
        with open(self.filename, mode="a", newline='', encoding="utf-8") as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            set_of_ids = self.get_all_ids()
            for item in list_of_items:
                if not item["id"] in set_of_ids:
                    print(f'nouvel item ajouté ! "{item["name"]}"')
                    csv_writer.writerow(item)
                    new_items.append(item)

        return new_items

    #rend opérationnel le scrapper
    def run(self):
        self.create_csv_file()
        self.run_driver()