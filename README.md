# CourseProject

Please fork this repository and paste the github link of your fork on Microsoft CMT. Detailed instructions are on Coursera under Week 1: Course Project Overview.

# Project Proposal
[project-proposal.pdf](project-proposal.pdf)

# Project Progress Report
[project-progress-report.pdf](project-progress-report.pdf)

# Documentation

## 1. Overview
This project contains two main components that together automatically identify in-demand skils through scraping and analysis of job postings from the job board [Indeed](www.indeed.com) for positions in New York, NY.

- `indeed_scraper.py`: Scrapes job postings in New York, NY, for a user-specified query. Specifically, it runs a user query on Indeed, scans results pages one by one, extracts job post links from each results page, and obtains and saves the content of each job post to a file (one per line). The output file is specified by the user. <!--This component optionally accepts a file containing a list of proxies to use when sending requests.--> *Can be used to run generic, user-specified queries and scrape results from the job board Indeed (For example, scrape job posts for software engineers, scrape job boards for data analysts, etc.)*.
- `keyword_extractor.py`: Extracts the top keywords from a collection of text documents. It accepts an input file of text documents where there is one document per line, extracts a number of top keywords as optionally specified by the user, and writes these keywords to a file that is specified by the user. *Can be used to generically extract top keywords from any collection of text (For example, top skills from job postings, top keywords from research papers, top themes in customer complaints, etc.).*

More generally, the component `indeed_scraper.py` can be used as a standalone script to scrape job postings at scale from Indeed *for any query* and `keyword_extractor.py` can be used both as a standalone script and as a module to extract top keywords (or phrases).

## 2. Implementation
### `indeed_scraper.py`
This module does the following:
1. In the main thread, creates a thread pool with a number of workers.
2. Executes the user query on Indeed and iterates through each page of the results one at a time.
3. For each page of results, extracts all job post links from that page and *feeds those links to the worker threads*, who will process specific job post links in parallel and will fetch the full content of each one.
4. The main thread continues to iterate through pages of results and passes specific job post links to the worker threads, while each worker thread continues to process specific job post links and captures the full content of each one.
5. Once the main thread has iterated through all pages of the search results, it waits for all the worker threads to finish processing the specific job post links that it has continuously passed them thus far.
6. Once all job posts have been processed, the thread pool terminates and the main thread writes all job posts to a file (each job post on its own line).

The logic described above is found mainly in the function `scrape_multithreaded(url, query, number_of_pages, results_per_page)`. Other important functions include:

`job_links_from_search(url, search_params)`:
- Obtains all job post links from the search results page specified by `url` and `search_params`.

`job_from_link(link)`:
- Obtains the content of the job post at the specified `link`.

`get_js_soup(url, params)`:
- Obtains a `BeautifulSoup` object for the page specified by `url` and `params` to be used for parsing HTML content.

Finally, all HTTP communication is carried out using python's `requests` module.

### `keyword_extractor.py`
This module does the following:
1. Ingests a text file where every line is a document of text.
2. Extracts the text from the input file and runs an algorithm on all the text to produce an optionally specified number of top keywords from the text. The algorithms used to produce the keywords is `TextRank`, as implemented by `pytextrank`, but other algorithms such as `YAKE`, as implemented by `pke`, are included as well unused functions in the codebase.
3. Outputs the top keywords to console or an optionally specified output file.

Note that this component can be used both as a standalone script as well as a module. Specifically, the class `KeywordExtractor` has a generic interface and can easily be reused in other settings:

`KeywordExtractor(input_file)`:

A `KeywordExtractor` is a class for extracting keywords from an input file of text where there is a text document on each line.
- `top_keywords([n])`: Extracts and returns a list of the top `n` keywords from the input file provided at construction.

## 3. Usage
### Installation
This package requires Python 3.0+.
It also requires the following external resources that can be obtained using:
```
pip install bs4
pip install spacy
pip install pytextrank
python -m spacy download en_core_web_sm
```

To install this package, clone the repository from github:
```
git clone https://github.com/myusername-2/CourseProject.git
cd CourseProject
```

### Usage Example
First, we scrape job posts from Indeed for ‘Software Engineer’ in New York, NY. The full job descriptions will be stored in `jobs.txt`, one job on each line.

```
python indeed_scraper.py --query 'Software Engineer' --pages 2 --results-per-page 25 --output-file jobs.txt
```

Then, we want to discover the most relevant skills in all these job descriptions. So we run the keyword extractor script as follows to discover the top 50 keywords:

```
python keyword_extractor.py -n 50 -o keywords.txt jobs.txt
```

The top 50 keywords will be stored in a file `keywords.txt`.

### API Usage
`keyword_extractor.py`:
```python
# Top 25 keywords from the collection in 'input.txt'
input_file = 'input.txt'
n = 25
keyword_extractor = KeywordExtractor(input_file)
top_keywords = keyword_extractor.top_keywords(n=n)
```

### Command Line Usage
`indeed_scraper.py`:
```
> python indeed_scraper.py --help
usage: indeed_scraper.py [-h] --output-file output_file --query query
                         [--pages pages] [--results-per-page results_per_page]

Scrape job posts from Indeed.

optional arguments:
  -h, --help            Show this help message and exit
  --pages pages         Number of pages of job results to scrape.
  --results-per-page results_per_page
                        Number of job results per scraped page.

required named arguments:
  --output-file output_file
                        Output file containing job descriptions matching the
                        query and with one job description per line.
  --query query         Query to search for jobs.
```

`keyword_extractor.py`:
```
> python keyword_extractor.py --help
usage: keyword_extractor.py [-h] [-n n] [-o output_file] input_file

Extract keywords from an input text.

positional arguments:
  input_file            Input file containing text. Each text document should
                        be on its own line.

optional arguments:
  -h, --help            show this help message and exit
  -n n                  Number of top keywords.
  -o output_file, --output-file output_file
                        Output file containing the top 'n' keywords in the
                        input text.
```