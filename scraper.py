import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from pandas import read_excel, DataFrame


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


def scrape_sub_image_urls(soup: BeautifulSoup):
    images = soup.find("div", {"data-main-product":True}).find("div", class_="no-js-hidden tm-product-image-container").find_all("img", {"width":"1500"})

    image_urls = []
    for image in images:
        image_urls.append(image.get("data-src").lstrip("//"))
        # print(image.get("data-src").lstrip("//"))

    return image_urls

def scrape_shortdescription(soup: BeautifulSoup):
    description = soup.find("ul", class_= "uk-list uk-list-disc uk-text-small uk-text-500")

    if description:
        return [li.text.strip() for li in description.find_all('li')]


def scrape_description_text(soup: BeautifulSoup):
    items = soup.find("div", class_="uk-position-relative uk-hidden", attrs={"data-filter": "group_1"}).find_all("div", class_="uk-section")

    descriptions = []
    for item in items:
        descriptions.append(item.text.strip())

    return descriptions


def scrape_description_images(soup: BeautifulSoup):
    images = (soup.find("div", class_="uk-position-relative uk-hidden", attrs={"data-filter": "group_1"})
             .find_all("div", class_="uk-container uk-container-large uk-section uk-padding-remove-bottom uk-text-center"))

    image_urls = []

    for image in images:
        image_url = image.find("source", media="(min-width: 1200px)").get("srcset").lstrip("//")
        image_urls.append(image_url)

    return image_urls


def scrape_price_original(soup: BeautifulSoup):
    normal_price_tag = soup.find("s", class_="uk-text-muted uk-text-500 price-item--regula uk-margin-small-left tm-linear-gradient-title")

    if normal_price_tag:
        return normal_price_tag.text.strip()


def scrape_price_discount(soup: BeautifulSoup):
    price_tag = soup.find("span", class_="uk-text-500 price-item--sale tm-linear-gradient-title")

    if price_tag:
        return price_tag.text.strip()


def scrape_specifications(soup: BeautifulSoup):
    specs = soup.find('div', {'data-tech-content': True})

    sections = specs.find_all("div", class_="uk-margin-medium")

    section_texts = []

    for section in sections:
        section_text = section.get_text(separator=" ", strip=True)
        section_texts.append(section_text)

    return section_texts


def scrape_faq(soup: BeautifulSoup):
    items = soup.find("div", {"data-filter": "group_4"}).find_all("li")

    # print(len(items))

    qa_list = []
    for item in items:
        # print(item.string)

        # Extract question
        question = item.find("a")

        # Extract answer
        answer = item.find("div")

        if question and answer:
            # Append question and answer to list
            qa_list.append(f"{question.text.strip()} A: {answer.text.strip()}")

    return qa_list


def scrape_url(url):
    response = requests.get(url)

    # with open("page.html", "r", encoding="utf-8") as file:
    #     html_content = file.read()

    soup = BeautifulSoup(response.content, "html5lib")

    return {
        "title": soup.find("title").text.strip(),
        "sku": scrape_sku(soup),
        "product_url": url,
        "main_image_url": scrape_main_image(soup),
        "sub_image_urls": scrape_sub_image_urls(soup),
        "shortdescription": scrape_shortdescription(soup),
        "description_text": scrape_description_text(soup),
        "description_images": scrape_description_images(soup),
        "price_original": scrape_price_original(soup),
        "price_discount": scrape_price_discount(soup),
        "specification": scrape_specifications(soup),
        "faq": scrape_faq(soup),
    }


def write_data_to_excel(scraped_data):
    # Check if data.xlsx exists, if not create it with appropriate headers
    try:
        output_df = read_excel("data.xlsx")
    except FileNotFoundError:
        output_df = DataFrame(
            columns=[
                "title",
                "sku",
                "product_url",
                "main_image_url",
                "sub_image_urls",
                "shortdescription",
                "description_text",
                "description_images",
                "price_original",
                "price_discount",
                "specification",
                "faq",
            ]
        )

    # Append the scraped data to the dataframe
    output_df = output_df._append(scraped_data, ignore_index=True)

    # Save the updated dataframe to data.xlsx
    output_df.to_excel("data.xlsx", index=False)


def get_urls():
    # Load the spreadsheet
    urls_df = read_excel("urls.xlsx")

    # Return the filtered URLs
    return urls_df["URLs"].tolist()


def run():
    # urls = [
    #     "https://www.bluettipower.eu/products/eb3a-pv120",
    #     "https://www.bluettipower.eu/products/eb3a-pv200",
    #     "https://www.bluettipower.eu/products/bluetti-m28-bayonet-3-pin-male-connector-for-ac500"
    # ]

    urls = get_urls()

    for url in urls:
        scrapped_data = scrape_url(url)
        write_data_to_excel(scrapped_data)
