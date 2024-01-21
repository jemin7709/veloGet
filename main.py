import time

from bs4 import BeautifulSoup
from selenium import webdriver

driver = webdriver.Chrome()

url = "https://velog.io/trending/week"
driver.get(url)
time.sleep(0.5)
html = driver.page_source
driver.quit()
soup = BeautifulSoup(html, "html.parser")

ul = soup.find("ul")
lis = ul.find_all("li")

for li in lis[:10]:
    link = li.find("a").get("href")
    title = li.find("h4").text
    author = li.find("b").text
    print(f"title: {title}\nlink: {link}\nauthor: {author}")
    print("=" * 10)
