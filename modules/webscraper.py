# import pandas as pd
# import urllib
import requests
from bs4 import BeautifulSoup
import re
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer


def getDataFromUrl(url, attempt=0):
    try:
        res = requests.get(url=url)
    except requests.RequestException as e:
        raise e
    html_page = res.content
    soup = BeautifulSoup(html_page, features="html.parser")
    text = soup.get_text()
    cleaned_text = re.sub(r"[\n\r\t]", "", text)
    return [cleaned_text]


main_content_tags = [
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "div",
    "span",
    "article",
    "section",
    "main",
    "ul",
    "ol",
    "li",
    "table",
    "tbody",
    "thead",
    "tr",
    "th",
    "td",
]


def urlScraper(url: list[str]) -> list[str]:
    # Load HTML
    loader = AsyncChromiumLoader(url)
    html = loader.load()
    # Transform
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        html, tags_to_extract=main_content_tags
    )
    # Result
    result = docs_transformed[0].page_content
    return [result]


def main(*args, **kwargs) -> None:
    print(type(urlScraper(url=["https://en.wikipedia.org/wiki/Blockchain"])))


if __name__ == "__main__":
    testURL = "https://en.wikipedia.org/wiki/Blockchain"
    print(type(getDataFromUrl(testURL)))
