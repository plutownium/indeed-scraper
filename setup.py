import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="indeedScraper",
    version="0.1.1",
    author="Roland Mackintosh",
    author_email="rolandmackintosh@outlook.com",
    description="A tool used to scrape & display data from Indeed",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/plutownium/indeed-scraper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)