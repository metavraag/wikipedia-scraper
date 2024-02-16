from src.scraper import WikipediaScraper
from concurrent.futures import ThreadPoolExecutor


def main():
    scraper = WikipediaScraper("https://country-leaders.onrender.com")
    countries = scraper.get_countries()
    scraper.get_leaders(countries)

    def fetch_first_paragraph(scraper, leader):
        # leader["first_paragraph"] = scraper.get_first_paragraph_api(
        leader["first_paragraph"] = scraper.get_first_paragraph(leader["wikipedia_url"])
        return leader

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(fetch_first_paragraph, scraper, leader)
            for country, leaders in scraper.leaders_data.items()
            for leader in leaders
        ]
        for future in futures:
            future.result()  # Wait for all

    scraper.to_csv_file("data/leaders_data_api.csv")
    # scraper.to_json_file("data/leaders_data_api.json")


if __name__ == "__main__":
    main()
