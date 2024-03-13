import requests
from bs4 import BeautifulSoup
import json
from pandas import read_excel, DataFrame
import traceback


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
    image_urls = []
    try:
        images = soup.find("div", {"data-main-product":True}).find("div", class_="no-js-hidden tm-product-image-container").find_all("img", {"width":"1500"})

        for image in images:
            image_urls.append(image.get("data-src").lstrip("//"))
    except Exception as e:
        pass

    try:
        images = soup.find("div", class_="Product__SlideshowNavScroller").find_all("a")

        for image in images:
            image_urls.append(image.get("href").lstrip("//"))
    except Exception as e:
        pass

    try:
        images = soup.find("div", {"data-section-type": "main-product-bucks"}).find_all("img", {"width":"2880"})
        for image in images:
            image_urls.append(image.get("data-src").lstrip("//"))
    except Exception as e:
        pass

    try:
        images = soup.find("div", class_="no-js-hidden tm-product-image-container").find_all("img", {"width":"2000"})
        for image in images:
            image_urls.append(image.get("data-src").lstrip("//"))
    except Exception as e:
        pass

    try:
        images = soup.find("div", class_="lg:col-span-4").find_all("img", {"width":"2000"})
        for image in images:
            image_urls.append(image.get("src").lstrip("//"))
    except Exception as e:
        pass

    return image_urls

def scrape_shortdescription(soup: BeautifulSoup):
    description = soup.find("ul", class_= "uk-list uk-list-disc uk-text-small uk-text-500")

    if description:
        return [li.text.strip() for li in description.find_all('li')]

    description = soup.find("div", class_="uk-display-block uk-margin-top")
    if description:
        return [li.text.strip() for li in description.find_all("li", {"data-mce-fragment":"1"})]

    description = soup.find("meta", {"name":"description"})
    if description:
        return description.get("content").strip()



def scrape_description_text(soup: BeautifulSoup):
    descriptions = []

    try:
        items = soup.find("div", class_="uk-position-relative uk-hidden", attrs={"data-filter": "group_1"}).find_all("div", class_="uk-section")

        for item in items:
            descriptions.append(item.text.strip())

    except Exception as e:
        pass

    try:
        #class="uk-section uk-section-default " data-filter="group_1"
        items = soup.find_all("div", class_="uk-section uk-section-default ", attrs={"data-filter": "group_1"})

        for item in items:
            descriptions.append(item.find("div", class_="uk-container uk-container-small").text.strip())

    except Exception as e:
        pass

    try:

        items = soup.find("div", class_="uk-position-relative uk-hidden", attrs={"data-filter": "group_1"}).find_all("div", class_="uk-section ")

        for item in items:
            descriptions.append(item.text.strip())

    except Exception as e:
        pass

    return descriptions


def scrape_description_images(soup: BeautifulSoup):
    image_urls = []

    try:
        images = (soup.find("div", class_="uk-position-relative uk-hidden", attrs={"data-filter": "group_1"})
             .find_all("div", class_="uk-container uk-container-large uk-section uk-padding-remove-bottom uk-text-center"))


        for image in images:
            image_url = image.find("source", media="(min-width: 1200px)").get("srcset").lstrip("//")
            image_urls.append(image_url)
    except Exception as e:
        pass
        # print("Description images not present")

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
    section_texts = []
    try:
        specs = soup.find('div', {'data-tech-content': True})

        sections = specs.find_all("div", class_="uk-margin-medium")


        for section in sections:
            section_text = section.get_text(separator=" ", strip=True)
            section_texts.append(section_text)

    except Exception as e:
        pass

    return section_texts


def scrape_faq(soup: BeautifulSoup):
    qa_list = []

    try:
        items = soup.find("div", {"data-filter": "group_4"}).find_all("li")

        for item in items:

            # Extract question
            question = item.find("a")

            # Extract answer
            answer = item.find("div")

            if question and answer:
                # Append question and answer to list
                qa_list.append(f"{question.text.strip()} A: {answer.text.strip()}")
    except Exception as e:
        pass

    try:
        items = soup.find_all("div", {"data-pf-type": "Accordion.Content.Wrapper"})

        for item in items:

            question = item.find("button").find("span")
            answer = item.find("div", {"div data-pf-expandable":"true"})

            if question and answer:
                qa_list.append(f"{question.text.strip()} A: {answer.text.strip()}")

    except Exception as e:
        pass

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
    # urls_df = urls_df[urls_df.iloc[:, 1] == 'x']

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
        try:
            scrapped_data = scrape_url(url)

        except Exception as e:
            print(url, e)
            traceback.print_exc()



        write_data_to_excel(scrapped_data)

run()