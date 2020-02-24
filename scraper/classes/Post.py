class Post:
    """A Posting is an object ...
        It has the attributes "job_title", "company", and "blurb", as well as "soup" and "actual_url".
    """

    def __init__(self, job_title, company, blurb, soup, url=None):
        self.title = job_title
        self.company = company
        self.blurb = blurb  # The blurb Indeed chose to use on the Page

        # Set these after initialization?
        self.salary = ""
        self.ez_apply = None

        self.actual_url = url
        self.soup = soup

    def print(self, show_company=False):
        if show_company:
            print("\n\nTitle: {}, \nCompany: {}, \nSummary: {}, \nLink: {}\n=========="
                  .format(self.title, self.company, self.blurb, self.actual_url))
        else:
            print("\n\nTitle: {}, \nSummary: {}, \nLink: {}\n=========="
                  .format(self.title, self.blurb, self.actual_url))