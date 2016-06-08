import threading

from util import util
from crawler import Spider
from database import SQLiteDatabase as Database
from database import DatabaseUtil

verbose = False

database_layout = DatabaseUtil.DatabaseLayout("ID, Title, Episode, Season, Date", "episode_id, title, episode, season, date")

class Show(threading.Thread):

    id = -1
    name = ""
    wikipedia_url = ""
    wikipedia_episodes_url = ""
    imdb_url = ""
    working_dir = ""
    state = ""

    spider = None
    database = None
    database_data = None

    def __init__(self, show_id, name, wikipedia_url, working_dir):
        threading.Thread.__init__(self, name=name)

        self.name = name
        self.id = show_id
        self.working_dir = working_dir
        self.wikipedia_url = wikipedia_url
        self.state = "Waiting"

        util.verbose_print("%35s Setting up" % ("[%s]" % self.name))

    def setup_database(self):
        self.database = Database.SQLiteDatabase("%s/databases/database.db" % self.working_dir)
        self.database.open_database()
        self.database.create_table(util.create_table_name(self.name), "ID INT, Title TEXT, Season INT, Episode INT, Date TEXT", True)
        self.database.close_database()

    def run(self):
        self.state = "Running"
        episode_data = self.crawl_wikipedia()

        self.database_data = DatabaseUtil.DatabaseData(util.create_table_name(self.name), episode_data, database_layout)
        util.verbose_print("%35s Finished gathering data" % ("[%s]" % self.name))

        self.state = "Finished"

    def remove_empty_episodes(self, data):
        for episode in data:
            if len(episode) == 0:
                data.remove(episode)
        return data

    def crawl_wikipedia(self):
        # util.verbose_print("\t\t - [%s] Crawling Wikipedia" % self.name)
        self.spider = Spider.Spider(self.name, self.wikipedia_url)
        episode_data = self.spider.run()
        episode_data = self.remove_empty_episodes(episode_data)
        if len(episode_data) != 0:
            print("%35s Seasons: %-3d | Episodes: %-3d" % (("[%s]" % self.name), episode_data[-1]['season'], episode_data[-1]['episode_id']))
        else:
            print("%35s ERROR, Broken Episode Data..." % ("[%s]" % self.name))
        return episode_data
        # self.spider.get_all_links()
        # self.get_imdb_url()
        # self.get_wikipedia_episodes_url()

    def crawl_imdb(self):
        util.verbose_print("\t\t - [%s] Crawling IMDB" % self.name)
        self.spider = Spider.Spider(self.name, self.imdb_url)
        self.spider.run()

    def get_wikipedia_episodes_url(self):
        self.wikipedia_episodes_url = self.spider.get_wikipedia_episodes_link()
        util.verbose_print("\t\t - [%s][Wiki]: %s" % (self.name, self.wikipedia_episodes_url))

    def get_imdb_url(self):
        self.imdb_url = self.spider.get_imdb_link()
        util.verbose_print("\t\t - [%s][IMDB]: %s" % (self.name, self.imdb_url))
