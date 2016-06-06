import os
import io

import show_list
from crawler import Show
from database import SQLiteDatabase as Database
from database import DatabaseUtil
from util import util

clean_slate = False
viewed_links = set()
links = set()
name = ""

spiders = []
spider_cap = 100
spider_count = 0

database_queue = []


def init(project_name):
    print("[Setup] Creating Project: '%s'" % project_name)

    create_directory("projects/%s" % project_name)
    create_directory("projects/%s/images" % project_name)
    create_directory("projects/%s/databases" % project_name)

    # Setup Database
    db = Database.SQLiteDatabase("projects/%s/databases/database.db" % project_name)
    db.open_database()
    db.create_table("Shows", "ShowID INT, Name TEXT, Wikipedia_URL TEXT, IMDB_URL TEXT, Trailer_URL TEXT", clean_slate)
    db.close_database()

    if clean_slate:
        create_database_from_file("projects/%s" % project_name)

    # shows = ["Gotham", "Silicon Valley", "Fargo", "Murder in the First", "Stitchers", "The Strain", "Fear the Walking Dead"]
    # update_shows("projects/%s" % project_name, shows)
    update_shows("projects/%s" % project_name, {})

    init_database_tables()

    spider_count = 0
    while len(spiders) != 0 or len(database_queue) != 0:
        spider_check(spider_count, spider_cap, db)

    print("No work to be done.. Exiting")
    db.close_database()

# Give the project directory and a list of shows. (if empty, all shows will be updated)
def update_shows(working_dir, shows):
    db = Database.SQLiteDatabase("%s/databases/database.db" % working_dir)
    db.open_database()
    data = db.read_from_table("Shows")
    count = 0
    all_shows = len(shows) == 0
    for show in data:
        if all_shows or str(show[1]) in shows:
            spiders.append(Show.Show(show[0], show[1], show[2], working_dir))

# Creates a database for each Show being crawled.
def init_database_tables():
    print("[Setup] Creating all tables...")
    for show in spiders:
        show.setup_database()
    print("[Setup] Succesfully created all tables")

# Main Loop, checks if spiders need to change job, and writes to database.
def spider_check(spider_count, spider_cap, database):
    if len(database_queue) != 0:
        data = database_queue.pop()
        data.write_to_database(database)

    for spider in spiders:
        if spider is None:
            spiders.remove(spider)
        else:
            if spider.state is "Finished":
                util.verbose_print("%30s [Spider] Finished, Adding to database queue" % ("[%s]" % spider.name))
                spider_count -= 1
                database_queue.append(spider.database_data)
                spiders.remove(spider)
            elif spider.state is "Waiting" and spider_cap >= spider_count:
                util.verbose_print("%30s [Spider] Inactive, Starting crawl" % ("[%s]" % spider.name))
                spider_count += 1
                spider.start()
    return True


def create_database_from_file(working_dir):
    database_layout = DatabaseUtil.DatabaseLayout("ID, Title, Episode, Season, Date", "episode_id, title, episode, season, date")
    db = Database.SQLiteDatabase("%s/databases/database.db" % working_dir)
    db.open_database()
    i = 0
    for show in show_list.shows:
        show_list.shows[show]['wiki'] = "http://en.wikipedia.org/wiki/%s" % show_list.shows[show]['wiki']
        show_list.shows[show]['imdb'] = "http://www.imdb.com/title/%s" % show_list.shows[show]['imdb']
        show_list.shows[show]['trailer'] = "http://www.youtube.com/watch?v=%s" % show_list.shows[show]['trailer']
        db.write_to_table("Shows", "ShowID, Name, Wikipedia_URL, IMDB_URL, Trailer_URL", "%d, \"%s\", \"%s\", \"%s\", \"%s\"" % (i, show, show_list.shows[show]['wiki'], show_list.shows[show]['imdb'], show_list.shows[show]['trailer']))
        i += 1
    db.commit()
    db.close_database()


def backup_database_to_file():
    print("TO BE DONE LATER")


def create_directory(directory):
    try:
        os.makedirs(directory)
    except FileExistsError:
        print("[Setup] Directory already exists: '%s'" % directory)
