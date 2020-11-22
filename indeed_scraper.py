import argparse
import concurrent.futures
import datetime
import logging
import random
import re
import sys
import time
import urllib
from collections import namedtuple
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

Job = namedtuple('Job', 'title description')

URL = 'http://www.indeed.com/jobs'
JOB_POST_URL = "http://www.indeed.com/viewjob"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:82.0) Gecko/20100101 Firefox/82.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'
]

def get_user_agent():
    user_agent = random.choice(USER_AGENTS)
    return user_agent

def get_headers():
    headers = {
        'User-Agent': get_user_agent(),
        'Referer': 'https://www.indeed.com/'
    }
    return headers

def get_search_params(query, start, results_per_page):
    params = {
        'q': query,
        'l': 'New York, NY',
        'start': str(start),
        'limit': str(results_per_page)
    }
    return params

def get_job_post_params(jk):
    params = {
        'jk': jk
    }
    return params

def full_url(base_url, params):
    if not params:
        return base_url
    return base_url + '?' + urlencode(params)

def get_js_soup(url, params):
    soup = None
    attempts = 5
    while attempts > 0:
        attempts -= 1
        logging.info(f"Retrieving '{full_url(url, params)}'")
        try:
            resp = requests.get(url, params=params,
                                headers = get_headers(),
                                timeout = 10)
            if resp.status_code != requests.codes.ok:
                logging.error(f"Error: [code: {resp.status_code}, reason: {resp.reason}, text: {resp.text}]")
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')
            return soup
        except Exception as exception:
            logging.error("Exception: " + str(exception))
            logging.error("Skipping.")
    return soup

def jobs_from_link(link):
    soup = get_js_soup(link, None)
    titles = soup.findAll('h1', attrs={'class': 'jobsearch-JobInfoHeader-title'})
    descriptions = soup.findAll('div', attrs={'class': 'jobsearch-jobDescriptionText'})
    jobs = []
    for description, title in zip(descriptions, titles):
        job_title = title.text.strip()
        job_description = description.text.strip().lower()
        job_description = re.sub('( +|-|\n)', ' ', job_description) # 'object-oriented', 'object  \n  oriented' -> 'object oriented'.
        job_description = re.sub('(\w+)\.(\w+)', '\g<1>\g<2>', job_description) # node.js -> nodejs
        job_description = re.sub('( +)', ' ', job_description)
        job_description = re.sub('( \.+)', '.', job_description)
        jobs.append(Job(title=job_title, description=job_description))
    return jobs

prev_page = -1
def job_links_from_search(url, search_params):
    soup = get_js_soup(url, search_params)
    page_count_boxes = soup.find_all('div', {'id':'searchCountPages'})
    if not page_count_boxes:
        return set()
    page_count = int(page_count_boxes[0].text.strip().split(' ')[1])
    global prev_page
    if page_count == prev_page:
        return set()
    prev_page = page_count
    jobs = soup.find_all('div', class_='jobsearch-SerpJobCard')
    job_links = set()
    for job in jobs:
        link = JOB_POST_URL + '?' + urlencode(get_job_post_params(job['data-jk']))
        job_links.add(link)
    return job_links

def scrape_multithreaded(url, query, number_of_pages, results_per_page):
    results_per_page = max(15, min(50, results_per_page))
    links = []
    previous_page_links = set()
    result = []
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:

        for i in range(0, number_of_pages):
            search_params = get_search_params(query, i * results_per_page, results_per_page)

            page_header = "Page #" + str(i) + " : " + url + '?' + urlencode(search_params, quote_via=urllib.parse.quote)
            logging.info("-" * len(page_header))
            logging.info(page_header)
            logging.info("-" * len(page_header))

            current_page_links = job_links_from_search(url, search_params)
            if not current_page_links or previous_page_links == current_page_links:
                logging.info("#"*100)
                logging.info(f"DUPLICATE (page {i})")
                logging.info("#"*100)
                break

            logging.info(f"  - Found {len(current_page_links)} jobs on this page:")
            for i, link in enumerate(current_page_links):
                logging.info(f"      [{i}] {link}")


            for link in current_page_links:
                futures.append(executor.submit(jobs_from_link, link))
            previous_page_links = current_page_links.copy()

        for pending in concurrent.futures.as_completed(futures):
            try:
                result.extend(pending.result())
            except Exception as e:
                logging.error("Error: Unable to obtain result for future: " + str(e))

    return result


def write_jobs(jobs, output_path):
    with open(output_path, "w") as outfile:
        for job in jobs:
            outfile.write(job.description + '\n')

def log_jobs(jobs):
    jobs_header = f"THERE ARE {len(jobs)} JOBS"
    logging.info("#" * len(jobs_header))
    logging.info(jobs_header)
    logging.info("#" * len(jobs_header))
    for i, job in enumerate(jobs):
        logging.info('-' * len(f"[Job #{i}] {job.title}"))
        logging.info(f"[Job #{i}] {job.title}")
        logging.info('-' * len(f"[Job #{i}] {job.title}"))
        logging.info(job.description)

def main():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(stream=sys.stdout, format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    parser = argparse.ArgumentParser(description='Scrape job posts from Indeed.')

    required = parser.add_argument_group('required named arguments')
    required.add_argument('--output-file', metavar='output_file', dest='output_file', type=str, required=True,
                          help='Output file containing job descriptions matching the query and with one job description per line.')
    required.add_argument('--query', metavar='query', type=str, required=True,
                          help='Query to search for jobs.')
    parser.add_argument('--pages', metavar='pages', type=int, required=False, default=1,
                          help='Number of pages of job results to scrape.')
    parser.add_argument('--results-per-page', metavar='results_per_page', type=int, required=False, default=15,
                          help='Number of job results per scraped page.')
    args = parser.parse_args()

    start = time.time()
    jobs = scrape_multithreaded(URL, args.query, args.pages, args.results_per_page)
    end = time.time()

    log_jobs(jobs)
    write_jobs(jobs, args.output_file)

    duration = str(datetime.timedelta(seconds=(end-start)))
    duration_header = f"Duration: {duration} ([H]H:MM:SS[.UUUUUU])"
    logging.info("-" * len(duration_header))
    logging.info(duration_header)
    logging.info("-" * len(duration_header))

if __name__ == '__main__':
    main()
