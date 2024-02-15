import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import time
import re
import json

# import cProfile
# cProfile.run('re.compile("foo|bar")')


class WikipediaScraper:
    def __init__(self, base_url: str) -> None:
        self.base_url: str = base_url
        self.country_endpoint: str = self.base_url + "/countries"
        self.leaders_endpoint: str = self.base_url + "/leaders"

        self.leaders_data: dict = {}

        self.cookies_endpoint: str = self.base_url + "/cookie"
        self.cookies = self.refresh_cookie()

    def __str__(self) -> str:
        """
        function that returns the string representation of the WikipediaScraper object.
        """
        return f"WikipediaScraper({self.base_url})"

    def refresh_cookie(self) -> object:
        """
        Function that will retrieve the cookies from the base url.

        :param cookie: An Object that contains the cookies from the given base url.
        :type requests.cookies.RequestsCookieJar
        :return: An Object that contains the cookies from the given root url (from
            the requests.cookies.RequestsCookieJar class).
        """
        return requests.get(self.cookies_endpoint).cookies

    def get_countries(self) -> list:
        return requests.get(self.country_endpoint, cookies=self.cookies).json()

    def get_leaders(self, country: str) -> None:
        self.leaders_data = {
            country: requests.get(
                self.leaders_endpoint, params={"country": country}, cookies=self.cookies
            ).json()
            for country in self.get_countries()
        }

    def get_first_paragraph(self, wikipedia_url: str) -> str:
        response = requests.get(wikipedia_url)
        soup = BeautifulSoup(response.text, "html.parser")
        first_p_with_b = soup.select_one("p:has(b)").text
        # todo: remove citation
        first_p_with_b = re.sub(r"\[.*\]", "", first_p_with_b)
        return first_p_with_b.strip()

    def to_json_file(self, filepath: str) -> None:
        with open(filepath, "w") as f:
            json.dump(self.leaders_data, f, indent=4)
        pass


if __name__ == "__main__":
    # import cProfile
    # cProfile.run("get_first_paragraph()", "profile_stats")
    # instantiate the WikipediaScraper object
    scraper = WikipediaScraper("https://country-leaders.onrender.com")
    # print(scraper)
    # print(scraper.cookies)
    # print(scraper.get_countries())
    countries = scraper.get_countries()
    print(countries)
    scraper.get_leaders(countries)
    for country, leaders in scraper.leaders_data.items():
        for leader in leaders:
            leader["first_paragraph"] = scraper.get_first_paragraph(
                leader["wikipedia_url"]
            )

    scraper.to_json_file("leaders_data2.json")
    # print(
    #     scraper.get_first_paragraph("https://en.wikipedia.org/wiki/George_Washington")
    # )
    # for country in countries:
    #     scraper.get_leaders(country)
    # print(scraper.leaders_data)
