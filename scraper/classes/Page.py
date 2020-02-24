class Page:
    """A Page is an object...
        Important to note that self.posts is a list of every Post found on the Page.
    """

    def __init__(self, page_num, num_of_jobs, page_links, page_url, soup):
        self.page_num = page_num
        self.num_of_jobs = num_of_jobs
        self.links = page_links

        self.page_url = page_url
        self.soup = soup

        self.posts = []
