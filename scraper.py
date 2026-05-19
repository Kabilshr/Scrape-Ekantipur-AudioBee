import json
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

BASE_URL = "https://ekantipur.com"
OUTPUT_PATH = Path("output.json")
# Limit the number of articles to scrape from the entertainment section
ENTERTAINMENT_ARTICLE_LIMIT = 5


def dismiss_pagegate_modal(page: Page) -> None:
    '''
    Dismiss the pagegate modal if it is visible
    '''
    if page.locator("#pagegate.show").count():
        page.locator('#pagegate button[data-bs-dismiss="modal"]').click()


def scrape_entertainment(page: Page) -> list[dict]:
    '''
    Scrape the entertainment articles from the page
    '''
    dismiss_pagegate_modal(page)

    page.wait_for_load_state("domcontentloaded")
    # Click on the entertainment category
    page.locator(".bottom-nav-wrap").locator("a").get_by_text("मनोरञ्जन", exact=True).first.click()
    
    # Get the cards for the entertainment articles
    cards = page.locator(".category-wrapper>.category")
    articles: list[dict] = []

    # Scrape up to 5 articles from the cards in the entertainment section
    for i in range(min(ENTERTAINMENT_ARTICLE_LIMIT, cards.count())):
        card = cards.nth(i)
        img_el = card.locator(".category-image > a > figure > img")
        # Some images might be lazy-loaded with data-src or similar attributes
        image_url = img_el.get_attribute("src") or img_el.get_attribute("data-src")
        title = card.locator(".category-description > h2").inner_text().strip()
        author_text = card.locator(".author-name>p>a").inner_text().strip()
        # If the author is not found, set it to "null"
        author = author_text if author_text else "null"
        # Append the article to the list
        articles.append(
            {
                "title": title,
                "image_url": image_url,
                "category": "मनोरञ्जन",
                "author": author,
            }
        )
    
    print(f"Scraped {len(articles)} entertainment articles")
    return articles


def scrape_cartoon_of_the_day(page: Page) -> dict:
    '''
    Scrape the cartoon of the day from the page
    '''
    # Dismiss the pagegate modal if it is visible
    dismiss_pagegate_modal(page)

    # Locate the section with the class 'e-section' containing 'कार्टुन' text
    section = page.locator("section.e-section").filter(has_text="कार्टुन")
    # Click on the link with text 'कार्टुन' to navigate to the cartoon page
    section.locator("a", has_text="कार्टुन").click()
    # Wait for the page to finish loading DOM content
    page.wait_for_load_state("domcontentloaded")
    
    # Select the first cartoon card
    cartoon = page.locator(".cartoon-wrapper").first
    # Locate the cartoon image element and extract the image URL (fallback to data-src)
    img_el = cartoon.locator(".cartoon-image > figure > a > img")
    image_url = img_el.get_attribute("src") or img_el.get_attribute("data-src")
    # Extract the cartoon title text
    title = cartoon.locator(".cartoon-description > p").first.inner_text().strip()

    # Try to extract the author, fallback to "null" if not found
    author_el = cartoon.locator(".author-name > p > a")
    author = author_el.first.inner_text().strip() if author_el.count() else "null"

    print(f"Title: {title}, Image URL: {image_url}, Author: {author}")
    return {
        "title": title,
        "image_url": image_url,
        "author": author,
    }

def write_output(entertainment_articles: list[dict], cartoon: dict, path: Path = OUTPUT_PATH) -> None:
    '''
    Write the output to a file
    '''
    data = {
        "entertainment": entertainment_articles,
        "cartoon_of_the_day": cartoon,
    }
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    '''
    Main function to scrape the page and write the output to a file
    '''
    with sync_playwright() as p:
        # Launch the browser in headless mode
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        # Navigate to the base URL and wait for the DOM to be loaded
        page.goto(BASE_URL, wait_until="domcontentloaded")

        # Scrape the entertainment articles
        entertainment_articles = scrape_entertainment(page)
        page.goto(BASE_URL, wait_until="domcontentloaded")
        # Scrape the cartoon of the day
        cartoon = scrape_cartoon_of_the_day(page)
        # Write the output to a file
        write_output(entertainment_articles, cartoon)

        browser.close()


if __name__ == "__main__":
    main()
