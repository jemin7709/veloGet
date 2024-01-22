import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from slack_bolt import App

import config

blocks = [
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": ""},
        "accessory": {
            "type": "image",
            "image_url": "",
            "alt_text": "",
        },
    },
    {"type": "divider"},
]


def scraping(driver: webdriver.Chrome, app: App, link):
    retry_count = 5
    delay = 3
    num_items = 5

    for i in range(retry_count):
        if i == retry_count - 1:
            app.client.chat_postMessage(channel="#에러", text="재시도 횟수 초과")
            print("재시도 횟수 초과")
            return False

        try:
            driver.get(link)
            time.sleep(3)
            html = driver.page_source
            driver.quit()

            soup = BeautifulSoup(html, "html.parser")
            ul = soup.find("ul")
            li_list = ul.find_all("li")

            for i, li in enumerate(li_list[:num_items]):
                link = li.find("a").get("href")
                title = li.find("h4").text
                author = li.find("b").text
                preview = li.find("p").text
                img_url = li.find("img").get("src")
                alt_text = li.find("img").get("alt")

                if len(preview) > 50:
                    preview = preview[:50] + "..."

                blocks[0]["text"][
                    "text"
                ] = f"*<{link}|{title}>*\nby {author}\n\n\n{preview}"
                blocks[0]["accessory"]["image_url"] = img_url
                blocks[0]["accessory"]["alt_text"] = alt_text

                app.client.chat_postMessage(
                    channel="#벨로그",
                    text="text",
                    blocks=blocks,
                    unfurl_links=False,
                    unfurl_media=False,
                )

                time.sleep(1)

            return True

        except Exception as e:
            print(e)
            time.sleep(delay)


if __name__ == "__main__":
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    app = App(token=config.slack_token)
    scraping(driver, app, config.velog + config.day)
