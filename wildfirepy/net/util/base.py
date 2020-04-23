import urllib
import urllib.request
from urllib.request import HTTPPasswordMgrWithDefaultRealm
from urllib.request import HTTPBasicAuthHandler, HTTPCookieProcessor
from http.cookiejar import CookieJar
import re

__all__ = ['URLOpenerWithRedirect', 'ModisHtmlParser', ]


class URLOpenerWithRedirect:

    def __init__(self, username='RaahulSingh', password='WildFire_Bad.100',
                 top_level_url="https://urs.earthdata.nasa.gov/"):
        auth_manager = HTTPPasswordMgrWithDefaultRealm()
        auth_manager.add_password('', top_level_url, username, password)
        handler = HTTPBasicAuthHandler(auth_manager)
        self.opener = urllib.request.build_opener(handler, HTTPCookieProcessor(CookieJar()))

    def __call__(self, url):
        return self.opener.open(url)


class ModisHtmlParser:

    def __init__(self):
        self.url_opener = URLOpenerWithRedirect()

    def __call__(self, url):
        self.html_content = self.url_opener(url).read().decode('cp1252')

    def get_all_hdf_files(self):
        return re.findall(r'href="(MCD64A1.*hdf)"', self.html_content)

    def get_all_dates(self):
        return re.findall(r'"(2.*)/"', self.html_content)

    def get_filename(self, h, v):
        h = str(h) if h > 9 else "0" + str(h)
        v = str(v) if v > 9 else "0" + str(v)

        r = re.compile(r'.*' + f'.(h{h}v{v}).')

        match = list(filter(r.match, self.get_all_hdf_files()))
        if len(match) == 0:
            raise UserWarning("No file exists for given coordinates.")

        return match[0]
