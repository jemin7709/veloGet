import argparse
import copy
import json
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


def scraping(driver: webdriver.Chrome, app: App, link, root):
    retry_count = 5
    delay = 3
    num_items = 5
    save_block = []

    for i in range(retry_count):
        if i == retry_count - 1:
            app.client.chat_postMessage(channel="#에러", text="velog 스크래핑 재시도 횟수 초과")
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

                save_block.append(copy.deepcopy(blocks))

            with open(root, "w", encoding="utf-8") as f:
                json.dump(save_block, f, ensure_ascii=False, indent=4)

            return True

        except Exception as e:
            print(e)
            time.sleep(delay)


def post(app: App, root):
    with open(root, "r", encoding="utf-8") as f:
        blocks = json.load(f)

    for block in blocks:
        app.client.chat_postMessage(
            channel="#벨로그",
            text="text",
            blocks=block,
            unfurl_links=False,
            unfurl_media=False,
        )

        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="velog 스크래핑 프로젝트")
    parser.add_argument("--scrap", action="store_true", help="스크래핑을 진행합니다")
    parser.add_argument("--post", action="store_true", help="포스팅을 진행합니다")
    parser.add_argument("--root", default="data.json", help="data.json 경로를 지정합니다")
    args = parser.parse_args()

    app = App(token=config.slack_token)
    if args.scrap:
        options = Options()
        options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=options)
        scraping(driver, app, config.velog + config.day, args.root)
    elif args.post:
        post(app, args.root)
