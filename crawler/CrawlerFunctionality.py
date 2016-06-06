from bs4 import BeautifulSoup as bs4
import requests
from util import util

def load_page(url):
    util.verbose_print("\t * [CrawlerFunc]: Attempting to load web page: '%s'" % url)
    page = requests.get(url, stream=True)
    return bs4(page.text, "html.parser")

def gather_links(page, parent):
    return filter(None, [create_full_link(get_link_from_element(link), parent) for link in page.find_all('a')])

def get_link_from_element(element):
    try:
        link = element['href']
        return link
    except KeyError:
        return "ERROR"

def find_episode_list_link(page):
    info_box = page.find('table', {'class': 'infobox'})
    if info_box != None:
        child = info_box.find('abbr', {'title': 'Number'})

        if child != None and child.parent != None and child.parent.parent != None:
            link = child.parent.parent.find_next('a')
            if link != None:
                return link['href']
    return None

def find_episode_link(show_name, page):
    episode_list = find_episode_list_link(page)
    if episode_list != None:
        if "#Episodes" not in episode_list:
            util.verbose_print("Found Episode Link: %s\n\t- Switching to new url..." % episode_list)
            page = load_page("http://en.wikipedia.org%s" % episode_list)

    episode_tables = page.find_all('table', {'class': 'wikiepisodetable'})
    if len(episode_tables) == 0:
        util.verbose_print("%s episode table is empty, trying solution 1" % show_name)
        episode_tables = page.find_all('table', {'class': 'wikitable'})

    season_num = 0
    last_date = -1
    total_episodes = 0
    episode_data = []
    for table in episode_tables:
        episode_num = 0
        season_num += 1
        episode_lines = table.find_all('tr', {'class': 'vevent'})
        for episode in episode_lines:

            # Finding the title of an episode
            title = episode.find('td', {'class': 'summary'})
            if title is not None:
                title = title.string
            else:
                title = "ERROR"
            date = episode.find('span', {'class': 'published'})

            # Finding the Date of an episode
            if date is not None:
                date = date.string
            else:
                dates = episode.find_all('td')
                valid_dates = []
                [valid_dates.append(possible_date) for possible_date in dates if len(str.split(str(possible_date))) == 3]
                date = "ERROR"
                for possible_date in valid_dates:
                    new_date = util.create_date_from(str.split(util.remove_character(possible_date.string, ','), " "))
                    if new_date is not None:
                        date = new_date

            # Finding out if the episode has released
            if last_date is -1 or compare_dates(date, last_date):
                episode_num += 1
                title = util.remove_character(title, "\"")
                title = util.remove_character(title, ",")
                total_episodes += 1
                episode_data.append({
                    'episode_id': total_episodes,
                    'season': season_num,
                    'episode': episode_num,
                    'date': str(date),
                    'title': str(title),
                })
                last_date = date
    return episode_data

def compare_dates(date1, date2):
    date1 = date1.split("-")
    date2 = date2.split("-")

    # If we weren't given a date.
    if date1 is "Error" or date2 is "Error":
        return True
    if len(date1) < 3 or len(date2) < 3:
        print("Something went wrong while comparing these dates:", date1, ", ", date2)
        return False

    # Otherwise:
    if date1[0] >= date2[0]:
        if date1[1] >= date2[1]:
            if date1[2] >= date2[2]:
                return True
            return date1[1] > date2[1]
        return date1[0] > date2[0]
    return False

def create_full_link(link, parent):
    if link is "ERROR":
        return
    if parent.endswith("/"):
        return "%s%s" % (parent, link)
    if "http://" not in link:
        index = parent.rfind("/")
        if "." not in parent[index:]:
            return "%s/%s" % (parent, link)
        return "%s/%s" % (parent[:index], link)
    return link
