import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

def scrape_sku(soup: BeautifulSoup):
    script_tags = soup.find_all("script", type="application/ld+json")

    for script_tag in script_tags:
        try:
            json_text = script_tag.string
            json_content = json.loads(json_text)
            if 'sku' in json_content:
                return json_content.get("sku")
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)

def scrape_main_image(soup: BeautifulSoup):
    script_tags = soup.find_all("script", type="application/ld+json")

    for script_tag in script_tags:
        try:
            json_text = script_tag.string
            json_content = json.loads(json_text)
            if 'image' in json_content:
                return json_content.get("image").get("url")
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)


def scrape_description_text(soup: BeautifulSoup):
    description = soup.find("ul", class_= "uk-list uk-list-disc uk-text-small uk-text-500")

    if description:
        return [li.text.strip() for li in description.find_all('li')]


def scrape_url(url):
    # response = requests.get(url)

    with open("page.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html5lib")

    title = soup.find("title").text.strip()
    sku = scrape_sku(soup)
    product_url = url
    main_image_url = scrape_main_image(soup)
    # sub_image_urls
    # short description
    description_text = scrape_description_text(soup)
    # description_images
    # priceOriginal
    # price_discount
    # specification
    # FAQ

    print(title)
    print(sku)
    print(product_url)
    print(main_image_url)
    print(description_text)



def run():
    urls = [
        "https://www.bluettipower.eu/products/eb3a-pv120",
        # "https://www.bluettipower.eu/products/eb3a-pv200",
        # "https://www.bluettipower.eu/products/bluetti-m28-bayonet-3-pin-male-connector-for-ac500"
    ]

    for url in urls:
        scrapped_data = scrape_url(url)