class Page:
    """A Page is an object...
        It has the the attributes "links", "page_num", ... what else?
    """

    def __init__(self, page_num, page_url, soup, page_links):
        self.page_num = page_num
        self.page_url = page_url
        self.soup = soup
        self.links = page_links

