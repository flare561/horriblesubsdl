from cfscrape import create_scraper, CloudflareScraper
from lxml.html import fromstring as lxmlfromstring
from os.path import realpath, join, dirname
import dill
import sys


SAVE_FILE = join(dirname(realpath(__file__)), 'scraper')

def get_session():
    try:
        with open(SAVE_FILE, 'rb') as f:
            sess = dill.load(f)
            assert(type(sess) is CloudflareScraper)
            return sess
    except Exception:
        return create_scraper()

def save_session(sess):
    try:
        with open(SAVE_FILE, 'wb') as f:
            dill.dump(sess, f)
    except Exception:
        pass

def get_pages(search, sess):
    nextid = 0
    while True:
        resp = sess.get("http://horriblesubs.info/lib/search.php",
                        params={"value": search, "nextid": nextid})
        if resp.content == b'':
            break
        if not resp.ok:
            yield b''
        else:
            yield resp.content
        nextid += 1

def build_html(search, sess):
    content = b"\n".join(list(get_pages(search, sess)))
    return lxmlfromstring(content)

def get_episodes(html, resolution):
    episodes = html.xpath(f"//div[contains(@class, '{resolution}') and "
                          f"contains(@class, 'release-links')]")

    def get_title_link_pair(element):
        title = element.xpath(".//td[contains(@class,"
                              "'dl-label')]/i")[0].text
        magnet = element.xpath(".//td[contains(@class, 'magnet')]"
                               "//a[@href]")[0].attrib["href"]
        return (title, magnet)

    return {title: magnet for title, magnet in
            map(get_title_link_pair, episodes)}

def fetch_episodes(searchtext, resolution):
    sess = get_session()
    content = build_html(searchtext, sess)
    save_session(sess)
    return get_episodes(content, resolution)

def add_torrents(tclient, torrents, directory):
    for _, magnet in torrents.items():
        tclient.add_torrent(magnet, download_dir=directory)

if __name__ == "__main__":
    print(fetch_episodes(" ".join(sys.argv[1:]), "720"))

