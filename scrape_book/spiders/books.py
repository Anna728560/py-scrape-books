import scrapy
from scrapy import Selector
from scrapy.http import Response

from selenium import webdriver
from selenium.webdriver.common.by import By


CONVERT_WORD_TO_DIGIT = {
        "Zero": 0,
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }


class BooksSpider(scrapy.Spider):
    """
    This spider scrapes book details from books.toscrape.com.
    """
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, **kwargs) -> None:
        """
        Initialize webdriver.
        """
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def parse(self, response: Response, **kwargs) -> None:
        """
        Parse the response.
        """
        for book in response.css(".product_pod"):
            yield from self._get_detail_book_info(response, book)

        next_button = response.css(".pager > li")[-1].css("a::attr(href)").get()

        if next_button is not None:
            next_page_url = response.urljoin(next_button)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def _get_detail_book_info(self, response: Response, book: Selector) -> None:
        """
        Extract detailed book information.
        """
        detailed_url = response.urljoin(book.css("h3 > a::attr(href)").get())
        self.driver.get(detailed_url)

        title = self.driver.find_element(By.CSS_SELECTOR, "h1").text
        price = float(self.driver.find_element(By.CSS_SELECTOR, ".price_color").text.replace("£", ""))
        amount_in_stock = self.driver.find_element(By.CSS_SELECTOR, ".instock.availability").text
        rating = self.driver.find_element(By.CSS_SELECTOR, "p.star-rating").get_attribute("class").split(" ")[1]
        category = self.driver.find_element(By.CSS_SELECTOR, "ul.breadcrumb > li:nth-last-child(2) > a").text
        description = self.driver.find_element(By.CSS_SELECTOR, ".product_page > p").text
        upc = self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) > td").text

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": CONVERT_WORD_TO_DIGIT[rating],
            "category": category,
            "description": description,
            "upc": upc
        }
