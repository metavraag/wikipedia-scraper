import requests
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import time
import re
import json
import csv


class WikipediaScraper:
    def __init__(self, base_url: str) -> None:
        self.session = requests.Session()
        self.base_url: str = base_url
        self.country_endpoint: str = self.base_url + "/countries"
        self.leaders_endpoint: str = self.base_url + "/leaders"

        self.leaders_data: dict = {}

        self.cookies_endpoint: str = self.base_url + "/cookie"
        self.cookies = self.refresh_cookie()
        self.sanitize = re.compile(r"\[.*\]")

    def __str__(self) -> str:
        return f"WikipediaScraper({self.base_url})"

    def refresh_cookie(self) -> object:
        return self.session.get(self.cookies_endpoint).cookies
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
        response = self.session.get(wikipedia_url)
        soup = BeautifulSoup(response.text, "html.parser")
        first_p_with_b = soup.select_one("p:has(b)").text
        # todo: remove citation
        # first_p_with_b = re.sub(r"\[.*\]", "", first_p_with_b)
        first_p_with_b = self.sanitize.sub("", first_p_with_b)
        return first_p_with_b.strip()

    def get_first_paragraph_api(self, wikipedia_url: str) -> str:
        # requests.get("https://en.wikipedia.org/api/rest_v1/page/summary/James_Monroe").json()['extract']
        wikipedia_api_url = wikipedia_url.replace(
            "org/wiki", "org/api/rest_v1/page/summary"
        )
        # first_paragraph = requests.get(wikipedia_api_url).json()["extract"]

        first_paragraph = self.session.get(wikipedia_api_url).json()["extract"]
        first_paragraph = self.sanitize.sub("", first_paragraph)

        return first_paragraph

    def to_json_file(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.leaders_data, f, ensure_ascii=False, indent=4)

    def to_csv_file(self, filename):
        # Define the header of the CSV file
        headers = [
            "id",
            "first_name",
            "last_name",
            "birth_date",
            "death_date",
            "place_of_birth",
            "wikipedia_url",
            "start_mandate",
            "end_mandate",
            "first_paragraph",
        ]

        # Open the file in write mode
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)

            # Write the header
            writer.writeheader()

            # Iterate through each country's leaders and write their data
            for country, leaders in self.leaders_data.items():
                for leader in leaders:
                    # Ensure each leader's data is written according to the header
                    writer.writerow({field: leader.get(field, "") for field in headers})


if __name__ == "__main__":

    def fetch_first_paragraph(scraper, leader):
        leader["first_paragraph"] = scraper.get_first_paragraph_api(
            leader["wikipedia_url"]
        )
        return leader

    scraper = WikipediaScraper("https://country-leaders.onrender.com")
    # print(scraper)
    # print(scraper.cookies)
    countries = scraper.get_countries()
    # print(countries)
    scraper.get_leaders(countries)

    for country, leaders in scraper.leaders_data.items():
        for leader in leaders:
            # leader["first_paragraph"] = scraper.get_first_paragraph(
            leader["first_paragraph"] = scraper.get_first_paragraph_api(
                leader["wikipedia_url"]
            )

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(fetch_first_paragraph, scraper, leader)
            for country, leaders in scraper.leaders_data.items()
            for leader in leaders
        ]
        for future in futures:
            future.result()  # Wait for all futures to complete

    scraper.to_json_file("data/leaders_data_api.json")
    scraper.to_csv_file("data/leaders_data_api.csv")
