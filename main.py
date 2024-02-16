from src.scraper import WikipediaScraper
from concurrent.futures import ThreadPoolExecutor


def main():
    """
    Main function orchestrating the scraping process. It initializes the scraper with a specific URL,
    fetches a list of countries and their leaders, and then concurrently fetches the first paragraph
    of each leader's Wikipedia page. The data is finally saved to a CSV file, with an option to save
    to a JSON file.
    """
    # Initialize the scraper with the base URL for the country-leaders data
    scraper = WikipediaScraper("https://country-leaders.onrender.com")

    # Fetch the list of countries available for scraping
    countries = scraper.get_countries()

    # Fetch the leaders for the available countries
    scraper.get_leaders(countries)

    def fetch_first_paragraph(scraper, leader):
        """
        Fetches the first paragraph of the leader's Wikipedia page.
        The paragraph is fetched using the scraper's get_first_paragraph_api method,
        taking the leader's Wikipedia URL as an argument.

        Parameters:
        - scraper: The WikipediaScraper instance to use for fetching the data.
        - leader: A dictionary containing the leader's details, including the Wikipedia URL.

        Returns:
        The leader dictionary updated with the first paragraph of their Wikipedia page.
        """
        # Fetch and assign the first paragraph of the leader's Wikipedia page
        leader["first_paragraph"] = scraper.get_first_paragraph_api(
            leader["wikipedia_url"]
        )
        return leader

    # Use ThreadPoolExecutor to fetch data concurrently for efficiency
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(fetch_first_paragraph, scraper, leader)
            for country, leaders in scraper.leaders_data.items()
            for leader in leaders
        ]
        # Wait for all fetching tasks to complete
        for future in futures:
            future.result()

    # Save the fetched data to a CSV file
    scraper.to_csv_file("data/leaders_data_api.csv")
    # Option to save to a JSON file, currently commented out
    # scraper.to_json_file("data/leaders_data_api.json")


if __name__ == "__main__":
    main()
