from wildfirepy.net.util import URLOpenerWithRedirect, ModisHtmlParser
from wildfirepy.coordinates.util import SinusoidalCoordinate
from requests.exceptions import HTTPError
from pathlib import Path
from urllib.error import HTTPError


__all__ = ['AbstractModisDownloader', 'ModisBurntDownloader']


class AbstractModisDownloader:

    def __init__(self):
        self.base_url = 'https://e4ftl01.cr.usgs.gov/'
        self.regex_traverser = ModisHtmlParser()
        self.converter = SinusoidalCoordinate()
        self.url_opener = URLOpenerWithRedirect()
        self.has_files = False

    def get_available_dates(self):
        self.regex_traverser(self.base_url)
        return self.regex_traverser.get_all_dates()

    def get_files_from_date(self, year, month):
        month = str(month) if month > 9 else "0" + str(month)
        date = f"{str(year)}.{month}.01/"
        self.regex_traverser(self.base_url + date)
        self.has_files = True
        return self.get_available_files()

    def get_available_files(self):
        return self.regex_traverser.get_all_hdf_files()

    def get_filename(self, latitude, longitude):
        h, v = self.converter(latitude, longitude)
        return self.regex_traverser.get_filename(h, v)

    def get_hdf(self, *, year, month, latitude, longitude):

        if not self.has_files:
            self.get_files_from_date(year, month)

        filename = self.get_filename(latitude, longitude)
        month = str(month) if month > 9 else "0" + str(month)
        date = f"{str(year)}.{month}.01/"
        url = self.base_url + date + filename
        return self.fetch(url=url, filename=filename)

    def get_xml(self, *, year, month, latitude, longitude):

        if not self.has_files:
            self.get_files_from_date(year, month)

        filename = self.get_filename(latitude, longitude) + ".xml"

        month = str(month) if month > 9 else "0" + str(month)
        date = f"{str(year)}.{month}.01/"
        url = self.base_url + date + filename
        return self.fetch(url=url, filename=filename)

    def get_jpg(self, *, year, month, latitude, longitude):

        if not self.has_files:
            self.get_files_from_date(year, month)

        filename = "BROWSE." + self.get_filename(latitude, longitude)[:-3] + "1.jpg"

        month = str(month) if month > 9 else "0" + str(month)
        date = f"{str(year)}.{month}.01/"
        url = self.base_url + date + filename
        return self.fetch(url=url, filename=filename)

    def fetch(self, url, path='./', filename='temp.hdf'):

        data_folder = Path(path)
        filename = data_folder / filename
        try:
            response = self.url_opener(url)
            print("Download Successful!")
            print("Writing file!")
            with open(filename, 'wb') as file:
                file.write(response.read())
            response.close()
            return filename.absolute().as_posix()

        except HTTPError as err:
            output = format(err)
            print(output)


class ModisBurntDownloader(AbstractModisDownloader):

    def __init__(self):
        super().__init__()
        self.base_url = self.base_url + "MOTA/MCD64A1.006/"
