import urllib.request
from bs4 import BeautifulSoup
from pymongo import MongoClient
import urllib.parse

client = MongoClient("mongodb://localhost:27017/")
db = client["web_crawler"]
pages_collection = db["pages"]

class Frontier:
    def __init__(self, initial_url):
        self.urls = [initial_url]
        self.visited = set()

    def done(self):
        return len(self.urls) == 0

    def nextURL(self):
        return self.urls.pop(0)

    def addURL(self, url):
        if url not in self.visited:
            self.urls.append(url)
            self.visited.add(url)

class Crawler:
    def __init__(self, frontier):
        self.frontier = frontier

    def retrieveHTML(self, url):
        response = urllib.request.urlopen(url)
        return response.read()

    def storePage(self, url, html):
        page_data = {
            "url": url,
            "html": html.decode("utf-8"),  
        }
        pages_collection.insert_one(page_data)

    def target_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        return bool(soup.find("h1", text="Permanent Faculty"))

    def run(self):
        while not self.frontier.done():
            url = self.frontier.nextURL()
            html = self.retrieveHTML(url)
            self.storePage(url, html)

            if self.target_page(html):
                self.frontier.urls = []
            else:
                soup = BeautifulSoup(html, "html.parser")
                for link in soup.find_all("a", href=True):
                    relative_url = link["href"]
                    if not relative_url.startswith("http"):
                        base_url = "https://www.cpp.edu/sci/computer-science/"
                        full_url = urllib.parse.urljoin(base_url, relative_url)
                    else:
                        full_url = relative_url
                    self.frontier.addURL(full_url)

initial_url = "https://www.cpp.edu/sci/computer-science/"
frontier = Frontier(initial_url)
crawler = Crawler(frontier)

crawler.run()
print("Crawling Completed")