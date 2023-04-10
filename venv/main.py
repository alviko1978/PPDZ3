from os import name
import requests
import fake_useragent
from bs4 import BeautifulSoup
import time
import json


def get_links(text):
    ua = fake_useragent.FakeUserAgent()
    data = requests.get(
        url = f"https://hh.ru/search/vacancy?area=1&area=2&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&text={text}&page=1",
        headers = {"user-agent":ua.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        page_count = int(soup.find("div", attrs={"class":"pager"}).find_all("span", recursive=False)[-1].find("a").find("span").text)
    except:
        return
    for page in range(page_count):
        try:
            data = requests.get(
                url=f"https://hh.ru/search/vacancy?area=1&area=2&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&text={text}&page={page}",
                headers={"user-agent": ua.random}
            )
            if data.status_code !=200:
                continue
            soup = BeautifulSoup(data.content, "lxml")
            for a in soup.find_all("a", attrs={"serp-item__title"}):
                yield f"{a.attrs['href'].split('?')[0]}"
        except Exception as e:
            print(f"{e}")
        time.sleep(1)


def get_vacancy(link):
    ua = fake_useragent.FakeUserAgent()
    data = requests.get(url=link, headers={"user-agent":ua.random})
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        title = soup.find(attrs={"class":"bloko-header-section-1"}).text
    except:
        title = ""

    try:
        salary = soup.find(attrs={"class": "bloko-header-section-2_lite"}).text.replace("\xa0","")
    except:
        salary = ""

    try:
        name_company = soup.find(attrs={"class": "bloko-link bloko-link_kind-tertiary"}).text.replace("\xa0", " ")
    except:
        name_company = ""

    try:
        name_city = soup.find(attrs={"data-qa": "vacancy-view-location"}).text
    except:
        name_city = ""

    try:
        skill = [tag.text for tag in soup.find(attrs={"class": "bloko-tag-list"})]
    except:
        skill = ""

    vacancy = {"link":link,
               "title":title,
               "salary":salary,
               "name_company":name_company,
               "name_city":name_city,
               "skill":skill
               }
    return vacancy

if __name__ == "__main__":
    data=[]
    for a in get_links("python"):
        vacancy = get_vacancy(a)
        if ("Django" or "Flask") in vacancy["skill"]:
            data.append(vacancy)
        time.sleep(1)
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)



