import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def fetch_figures_from_js_enabled_url(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(5)  # Adjust if needed
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        figure_data = []

        figures = soup.find_all('figure')

        for figure in figures:
            img_tag = figure.find('div').find('img')
            caption_tag = figure.find('figcaption')

            if img_tag and caption_tag:
                img_src = img_tag.get('src')
                caption_text = caption_tag.get_text(strip=True)

                figure_data.append({
                    'image_src': img_src,
                    'caption': caption_text
                })

        # Ensure we're getting valid data
        if figure_data:
            with open('figure_data.json', 'w') as json_file:
                json.dump(figure_data, json_file, ensure_ascii=False, indent=4)

            print("Data saved successfully.")
        else:
            print("No data found to save.")

    finally:
        driver.quit()

url = input("Enter the URL: ")
fetch_figures_from_js_enabled_url(url)
