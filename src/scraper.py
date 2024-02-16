# Importing necessary libraries for the documentation
import requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import re
import json
import csv


class ScraperException(Exception):
    """
    Exception class for handling errors during the scraping process.

    Attributes:
        message (str): Human-readable description of the error.
    """

    def __init__(self, message="An error occurred in the scraping process"):
        self.message = message
        super().__init__(self.message)


class WikipediaScraper:
    """
    A class for scraping data from Wikipedia based on provided URLs.

    Attributes:
        base_url (str): The base URL for the Wikipedia or related site to scrape.
        session (requests.Session): Session object for making HTTP requests.
        country_endpoint (str): Endpoint URL for fetching country data.
        leaders_endpoint (str): Endpoint URL for fetching leaders data.
        cookies_endpoint (str): Endpoint URL for fetching cookies.
        cookies (RequestsCookieJar): Cookies obtained from the cookies endpoint.
        leaders_data (dict): Dictionary storing leaders data fetched.
        sanitize (re.Pattern): Regular expression pattern for sanitizing text.
    """

    def __init__(self, base_url: str) -> None:
        """
        Initializes the WikipediaScraper with a base URL.

        Parameters:
            base_url (str): The base URL for the scraping operations.
        """
        self.session = requests.Session()
        self.base_url: str = base_url
        self.country_endpoint: str = self.base_url + "/countries"
        self.leaders_endpoint: str = self.base_url + "/leaders"
        self.cookies_endpoint: str = self.base_url + "/cookie"
        self.cookies = self.refresh_cookie()
        self.leaders_data: dict = {}
        self.sanitize = re.compile(r"\[.*\]")

    def __str__(self) -> str:
        """
        String representation of the WikipediaScraper instance.

        Returns:
            str: Representation of the scraper including the base URL.
        """
        return f"WikipediaScraper({self.base_url})"

    def refresh_cookie(self) -> object:
        """
        Refreshes and returns the session cookies from the cookies endpoint.

        Returns:
            RequestsCookieJar: The cookies obtained from the cookies endpoint.
        """
        return self.session.get(self.cookies_endpoint).cookies

    def get_countries(self) -> list:
        """
        Fetches and returns a list of countries from the country endpoint.

        Returns:
            list: A list of countries.

        Raises:
            ScraperException: If an error occurs during the fetch operation.
        """
        try:
            response = self.session.get(self.country_endpoint)
            response.raise_for_status()  # Checks for HTTP errors.
            return response.json()
        except Exception as e:
            raise ScraperException(f"Error fetching countries: {e}")

    def get_leaders(self, country: str) -> None:
        """
        Fetches and stores leaders data for the given country.

        Parameters:
            country (str): The country for which leaders data is fetched.
        """
        self.leaders_data = {
            country: self.session.get(
                self.leaders_endpoint,
                params={"country": country},
            ).json()
            for country in self.get_countries()
        }

    def get_first_paragraph(self, wikipedia_url: str) -> str:
        """
        Fetches and returns the first paragraph of a Wikipedia page.

        Parameters:
            wikipedia_url (str): URL of the Wikipedia page.

        Returns:
            str: The first paragraph text of the given Wikipedia page.
        """
        response = self.session.get(wikipedia_url)
        soup = BeautifulSoup(response.text, "html.parser")
        first_p_with_b = soup.select_one("p:has(b)").text
        first_p_with_b = self.sanitize.sub("", first_p_with_b)
        return first_p_with_b.strip()

    def get_first_paragraph_api(self, wikipedia_url: str) -> str:
        """
        Fetches the first paragraph of a Wikipedia page using the Wikipedia API.

        Parameters:
            wikipedia_url (str): URL of the Wikipedia page.

        Returns:
            str: The first paragraph text of the given Wikipedia page.
        """
        wikipedia_api_url = wikipedia_url.replace(
            "org/wiki", "org/api/rest_v1/page/summary"
        )
        first_paragraph = self.session.get(wikipedia_api_url).json()["extract"]
        first_paragraph = self.sanitize.sub("", first_paragraph)
        return first_paragraph

    def to_json_file(self, filepath: str) -> None:
        """
        Writes the leaders data to a JSON file.

        Parameters:
            filepath (str): The path of the file where data will be written.
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.leaders_data, f, ensure_ascii=False, indent=4)

    def to_csv_file(self, filename: str) -> None:
        """
        Writes the leaders data to a CSV file.

        Parameters:
            filename (str): The name of the file where data will be written.
        """
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
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            for country, leaders in self.leaders_data.items():
                for leader in leaders:
                    writer.writerow({field: leader.get(field, "") for field in headers})


# Example function outside of class to demonstrate fetching and processing
def fetch_first_paragraph(scraper, leader):
    """
    Fetches and updates a leader's dictionary with their first paragraph from Wikipedia.

    Parameters:
        scraper (WikipediaScraper): The scraper instance used for fetching.
        leader (dict): Dictionary representing the leader to update.

    Returns:
        dict: The updated leader dictionary with the first paragraph added.
    """
    leader["first_paragraph"] = scraper.get_first_paragraph_api(leader["wikipedia_url"])
    return leader


# Example of using the scraper
if __name__ == "__main__":
    scraper = WikipediaScraper("https://country-leaders.onrender.com")
    countries = scraper.get_countries()
    scraper.get_leaders(countries)

    # Using ThreadPoolExecutor to fetch first paragraphs concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(fetch_first_paragraph, scraper, leader)
            for country, leaders in scraper.leaders_data.items()
            for leader in leaders
        ]
        for future in futures:
            future.result()  # Wait for all to complete

    # Example of writing data to CSV
    scraper.to_csv_file("data/leaders_data_api.csv")
