import requests
from bs4 import BeautifulSoup
import re


def get_leaders():
    root_url = "https://country-leaders.onrender.com"
    status_url = f"{root_url}/status"
    cooke_url = f"{root_url}/cookie"
    # check_url = f"{root_url}/check"
    contries_url = f"{root_url}/countries"
    leaders_url = f"{root_url}/leaders"

    cookie_response = requests.get(cooke_url)
    cookies = cookie_response.cookies
    # print(cookies)

    # status_response = requests.get(status_url)
    status_response = requests.get(status_url, cookies=cookies)

    print(status_response.json())

    countries = requests.get(contries_url, cookies=cookies).json()
    print(countries)

    leaders_per_country = {}
    leaders_per_country = {
        country: requests.get(
            leaders_url, params={"country": country}, cookies=cookies
        ).json()
        for country in countries
    }
    for country, leaders in leaders_per_country.items():
        for leader in leaders:
            print(leader["last_name"])
            w_url = leader["wikipedia_url"]
            leader["first_paragraph"] = get_first_paragraph(w_url)

    return leaders_per_country


# print(leaders_per_country())
# print(len(leaders_per_country))
def get_first_paragraph(wikipedia_url):
    print(wikipedia_url)
    response = requests.get(wikipedia_url)
    soup = BeautifulSoup(response.text, "html.parser")
    first_p_with_b = soup.select_one("p:has(b)").text
    # todo: remove citation
    first_p_with_b = re.sub(r"\[.*\]", "", first_p_with_b)
    return first_p_with_b.strip()


if __name__ == "__main__":
    print(len(get_leaders()))
