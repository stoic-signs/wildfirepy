from wildfirepy.net.util import URLOpenerWithRedirect, ModisHtmlParser
from wildfirepy.coordinates.util import SinusoidalCoordinate
from pathlib import Path
from urllib.error import HTTPError


__all__ = ['AbstractModisDownloader', 'ModisBurntAreaDownloader']


class AbstractModisDownloader:
    """
    Description
    -----------
    An Abstract Base Class Downloader for MODIS products.
    """
    def __init__(self):
        self.base_url = 'https://e4ftl01.cr.usgs.gov/'
        self.regex_traverser = ModisHtmlParser()
        self.converter = SinusoidalCoordinate()
        self.url_opener = URLOpenerWithRedirect()
        self.has_files = False

    def get_available_dates(self):
        """
        Returns dates for which data is available.
        """
        self.regex_traverser(self.base_url)
        return self.regex_traverser.get_all_dates()

    def get_files_from_date(self, year, month):
        """
        Returns names of all available files.

        Parameters
        ----------
        year: `int`
            Year for which filenames are to be retrieved.
        month: `int`
            Month for which filenames are to be retrieved.
        """
        month = str(month) if month > 9 else "0" + str(month)
        date = f"{str(year)}.{month}.01/"
        self.regex_traverser(self.base_url + date)
        self.has_files = True
        return self.regex_traverser.get_all_files()

    def get_available_jpg_files(self):
        """
        Returns names of available jpg files.
        """
        return self.regex_traverser.get_all_jpg_files()

    def get_available_xml_files(self):
        """
        Returns names of available xml files.
        """
        return self.regex_traverser.get_all_xml_files()

    def get_available_hdf_files(self):
        """
        Returns names of available hdf files.
        """
        return self.regex_traverser.get_all_hdf_files()

    def get_filename(self, latitude, longitude):
        """
        Returns name of file for given latitude and longitude.

        Parameters
        ----------
        latitude: `float`
            latitude of the observation.
        longitude: `float`
            longitude of the observation.
        """
        h, v = self.converter(latitude, longitude)
        return self.regex_traverser.get_filename(h, v)

    def get_hdf(self, *, year, month, latitude, longitude, **kwargs):
        """
        Downloads the `hdf` file and stores it on the disk.

        Parameters
        ----------
        year: `int`
            Year of the observation.
        month: `int`
            Month of the observation.
        latitude: `float`
            latitude of the observation.
        longitude: `float`
            longitude of the observation.
        kwargs: keyword arguments to be passed to `AbstractModisDownloader.fetch`

        Returns
        -------
        path: `str`
            Absolute path to the downloaded `hdf` file.
        """
        if not self.has_files:
            self.get_files_from_date(year, month)

        filename = self.get_filename(latitude, longitude)
        month = str(month) if month > 9 else "0" + str(month)
        date = f"{str(year)}.{month}.01/"
        url = self.base_url + date + filename
        return self.fetch(url=url, filename=filename, **kwargs)

    def get_xml(self, *, year, month, latitude, longitude, **kwargs):
        """
        Downloads the `xml` file and stores it on the disk.

        Parameters
        ----------
        year: `int`
            Year of the observation.
        month: `int`
            Month of the observation.
        latitude: `float`
            latitude of the observation.
        longitude: `float`
            longitude of the observation.
        kwargs: keyword arguments to be passed to `AbstractModisDownloader.fetch`

        Returns
        -------
        path: `str`
            Absolute path to the downloaded `xml` file.
        """
        if not self.has_files:
            self.get_files_from_date(year, month)

        filename = self.get_filename(latitude, longitude) + ".xml"

        month = str(month) if month > 9 else "0" + str(month)
        date = f"{str(year)}.{month}.01/"
        url = self.base_url + date + filename
        return self.fetch(url=url, filename=filename, **kwargs)

    def get_jpg(self, *, year, month, latitude, longitude, **kwargs):
        """
        Downloads the `jpg` file and stores it on the disk.

        Parameters
        ----------
        year: `int`
            Year of the observation.
        month: `int`
            Month of the observation.
        latitude: `float`
            latitude of the observation.
        longitude: `float`
            longitude of the observation.
        kwargs: keyword arguments to be passed to `AbstractModisDownloader.fetch`

        Returns
        -------
        path: `str`
            Absolute path to the downloaded `jpg` file.
        """
        if not self.has_files:
            self.get_files_from_date(year, month)

        filename = "BROWSE." + self.get_filename(latitude, longitude)[:-3] + "1.jpg"

        month = str(month) if month > 9 else "0" + str(month)
        date = f"{str(year)}.{month}.01/"
        url = self.base_url + date + filename
        return self.fetch(url=url, filename=filename, **kwargs)

    def fetch(self, url, path='./', filename='temp.hdf'):
        """
        Fetches data from `url`.

        Parameters
        ----------
        url: `str`
            URL to get the data from.
        path: `str`
            path to store the downladed file.
        filename: `str`
            name of the downladed file.

        Returns
        -------
        path: `str`
            Absolute path to the downloaded `hdf` file.
        """
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


class ModisBurntAreaDownloader(AbstractModisDownloader):
    """
    Description
    -----------
    MODIS Class for `MCD64A1`, i.e., Burnt Area.
    By default downloads data from the 6th collection.
    """
    def __init__(self, collection='006'):
        super().__init__()
        self.base_url = self.base_url + f"MOTA/MCD64A1.{collection}/"
