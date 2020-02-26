# ### Check the URL of ONE post object just to make sure we got the data from the right Card
        if count == 0:
            redundant_check = requests.get(my_post_objects[0].url)
            redundant_soup = BeautifulSoup(redundant_check, "html.parser")

            # Get Post title, company and pay, see if they match what we got (if 2/3 match, we're good)
            r_title = redundant_soup.find("h3", {"class": "jobsearch-JobInfoHeader-title"}).decode_contents()
            r_company = redundant_soup.find("div", {"class": "jobsearch-InlineCompanyRating"})\
                .find("div").decode_contents()
            r_pay = redundant_soup.find("span", {"class": "jobsearch-JobMetadataHeader-iconLabel"})
            if r_pay:
                r_pay = r_pay.decode_contents()
            else:
                r_pay = None

            # Compare Post data from the Post to Post data from the Page...
            if r_title == post_title and post_company == r_company and post_pay == r_pay:
                # Definitely added the data to the right object...
            if r_title == post_title and post_company == r_company:

            if r_title == post_title and post_pay == r_pay:

            if post_company == r_company and post_pay == r_pay:
