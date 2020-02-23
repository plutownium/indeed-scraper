class Posting:
    """A Posting is an object ...
        It has the attributes "job_title", "company", and "summary".
    """

    def __init__(self, job_title, company, summary, url=None):
        self.title = job_title
        self.company = company
        self.summary = summary
        self.actual_url = url

        # Set these after initialization?
        self.salary = ""
        self.ez_apply = None

    def print(self, show_company=False):
        if show_company:
            print("\n\nTitle: {}, \nCompany: {}, \nSummary: {}, \nLink: {}\n=========="
                  .format(self.title, self.company, self.summary, self.actual_url))
        else:
            print("\n\nTitle: {}, \nSummary: {}, \nLink: {}\n=========="
                  .format(self.title, self.summary, self.actual_url))