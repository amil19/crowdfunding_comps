import requests
import bs4
from typing import Literal

class KS_Datasets():
    """Class to retrieve list of Kickstarter datasets.
    """

    ks_site = r"https://webrobots.io/kickstarter-datasets/"

    def __init__(self):
        """Loads Kickstarter archive website and extracts all JSON links.
        """
        soup = self.load_and_soup_site(self.ks_site)
        self.archive_links = self.get_links(soup,'json')


    @staticmethod
    def load_and_soup_site(website: str) -> bs4.BeautifulSoup:
        """Connects to a website and creates a 'soup' object of its HTML.

        Args:
            website (str): URL for website to load.

        Returns:
            bs4.BeautifulSoup: Soup object containing the HTML of a site.
        """
        response = requests.get(website)
        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.content,'html.parser')
            print("Successfully souped site.")
            return soup
        else:
            print(f"Unable to soup site.\nResponse status code: {response.status_code}")

    @staticmethod
    def get_links(soup: bs4.BeautifulSoup, file_type:Literal['json','csv']=None)-> list[str]:
        """Creates a list containing all links from a given webpage.

        Args:
            soup (bs4.BeautifulSoup): An HTML parsed 'soup' object.
            file_type (Literal['json','csv'], optional): Parameter to specify a file_type to search for in links. Defaults to None. 
            If None is selected, will return all links, regardless of type.

        Returns:
            list[str]: List of links from a given webpage.
        """

        if file_type is None:
            link_list = [a['href'] for a in soup.find_all('a',href=True) if 'aws' in a['href']]
        else:
            link_list = [a['href'] for a in soup.find_all('a',href=True) if 'aws' in a['href'] and file_type in a['href']]
        print(f"Found {len(link_list)} links")
        return link_list