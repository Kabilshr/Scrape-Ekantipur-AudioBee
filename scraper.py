import json
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

BASE_URL = "https://ekantipur.com"
OUTPUT_PATH = Path("output.json")
ENTERTAINMENT_ARTICLE_LIMIT = 5


def dismiss_pagegate_modal(page: Page) -> None:
    if page.locator("#pagegate.show").count():
        page.locator('#pagegate button[data-bs-dismiss="modal"]').click()


def scrape_entertainment(page: Page) -> list[dict]:
    dismiss_pagegate_modal(page)

    page.wait_for_load_state("domcontentloaded")

    page.locator(".bottom-nav-wrap").locator("a").get_by_text("मनोरञ्जन", exact=True).first.click()
    

    cards = page.locator(".category-wrapper>.category")
    articles: list[dict] = []

    for i in range(min(ENTERTAINMENT_ARTICLE_LIMIT, cards.count())):
        card = cards.nth(i)
        img_el = card.locator(".category-image > a > figure > img")
        # Some images might be lazy-loaded with data-src or similar attributes
        image_url = img_el.get_attribute("src") or img_el.get_attribute("data-src")
        title = card.locator(".category-description > h2").inner_text().strip()
        author_text = card.locator(".author-name>p>a").inner_text().strip()
        author = author_text if author_text else "null"
        articles.append(
            {
                "title": title,
                "image_url": image_url,
                "category": "मनोरञ्जन",
                "author": author,
            }
        )
    print(articles)
    

    return articles


def scrape_cartoon_of_the_day(page: Page) -> dict:

    dismiss_pagegate_modal(page)
    section = page.locator("section.e-section").filter(has_text="कार्टुन")
    section.locator("a", has_text="कार्टुन").click()
    page.wait_for_load_state("domcontentloaded")

    cartoon = page.locator(".cartoon-wrapper").first
    img_el = cartoon.locator(".cartoon-image > figure > a > img")
    image_url = img_el.get_attribute("src") or img_el.get_attribute("data-src")
    title = cartoon.locator(".cartoon-description > p").first.inner_text().strip()

    author_el = cartoon.locator(".author-name > p > a")
    author = author_el.first.inner_text().strip() if author_el.count() else "null"

    print(f"Title: {title}, Image URL: {image_url}, Author: {author}")
    return {
        "title": title,
        "image_url": image_url,
        "author": author,
    }


def write_output(
    entertainment_articles: list[dict],
    cartoon: dict,
    path: Path = OUTPUT_PATH,
) -> None:
    data = {
        "entertainment": entertainment_articles,
        "cartoon_of_the_day": cartoon,
    }
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(BASE_URL, wait_until="domcontentloaded")

        entertainment_articles = scrape_entertainment(page)
        page.goto(BASE_URL, wait_until="domcontentloaded")
        cartoon = scrape_cartoon_of_the_day(page)

        write_output(entertainment_articles, cartoon)

        browser.close()


if __name__ == "__main__":
    main()
