import threading
from crawler import CrawlerFunctionality as Crawl

class Spider(threading.Thread):

    kill = False
    output = []

    def __init__(self, name="...", url="..."):
        threading.Thread.__init__(self, name=name)
        self.name = name
        self.url = url
        self.page = None
        self.running = False
        self.output = []

    def destroy(self):
        return self.output

    # Main function to be run (called in new thread when using spider.start())
    def run(self):
        self.running = True
        self.page = Crawl.load_page(self.url)
        return Crawl.find_episode_link(self.name, self.page)

    def get_all_links(self):
        [self.output.append(link) for link in Crawl.gather_links(self.page, self.url) if link is not None]

    # Returns all Wikipedia.com links found
    def get_wikipedia_episodes_link(self):
        return self.url

    # Returns all imdb.com links found
    def get_imdb_link(self):
        if "wiki" in self.url:
            for link in self.output:
                if "imdb.com" in link:
                    if "episodes" in link or link.endswith("/"):
                        index = link.rfind("/")
                        return link[0:index]
                    return link
