import json
import os
import time

from datetime import datetime

import feedparser


def get_rules() -> dict:
    """
    Will obtain the rules file

    :return:
    """
    rules_file = os.getenv('RULES_FILE', 'basic.json')
    with open(rules_file, 'r') as rule_file_pointer:
        rules = json.loads(rule_file_pointer.read())
    return rules


class Job:
    def __init__(self, title: str, details: str, created: datetime, url: str):
        self.__title = title
        self.__details = details
        self.__created = created
        self.__url = url


class JobMonitor:
    def __init__(self):
        self.__total_entries = 0
        self.__site_url = None
        self.__ignored_titles = 0
        self.__effective_entries = []

    @property
    def effective_entries(self) -> list:
        return self.__effective_entries

    @effective_entries.setter
    def effective_entries(self, job: dict):
        created = datetime.fromtimestamp(time.mktime(job.get('published_parsed')))
        job_data = {
            "title": job.get('title'),
            "created": created,
            "url": job.get('link'),
            "details": job.get('summary')
        }

        self.__effective_entries.append(Job(**job_data))

    @property
    def ignored_titles(self) -> int:
        return self.__ignored_titles

    @ignored_titles.setter
    def ignored_titles(self, ignored_titles: int):
        self.__ignored_titles = ignored_titles

    @property
    def total_entries(self) -> int:
        return self.__total_entries

    @total_entries.setter
    def total_entries(self, total_entries: int):
        self.__total_entries = total_entries

    @property
    def site_url(self) -> str:
        return self.__site_url

    @site_url.setter
    def site_url(self, site_url: str):
        self.__site_url = site_url


def job_title_collector(rule_list: list):
    """
    With the received title analyze and ignore
    a job based in the title.
    Example: `rockstar php developer`, `ninja developer`
    will be totally ignored
    :param rule_list:

    :return:

    """
    bad_titles = rule_list.get('title').get('avoid')
    while True:
        job = yield
        job_title = job.title.split(' ')
        bad_title_pattern = set(job_title).intersection(bad_titles)
        if not bad_title_pattern:
            yield job


def fetch_data(site_url: str, monitor: JobMonitor, title_reader):
    """
    Read a target_site and extract the information
    :param site_url:
    :param monitor: JobMonitor used to count how many jobs we read
    :param title_reader: coroutine
    :return: list

    """

    feed = feedparser.parse(site_url)
    print(f"I have a total of {len(feed.entries)} feed items")
    for job_entry in feed.entries:
        monitor.total_entries += 1
        good_job = title_reader.send(job_entry)
        if good_job:
            monitor.effective_entries = good_job
        else:
            monitor.ignored_titles += 1

    title_reader.close()


if __name__ == '__main__':
    rules = get_rules()
    target_site = os.getenv('SITE', 'https://remoteok.io/remote-jobs.rss')
    job_monitor = JobMonitor()
    job_monitor.site_url = target_site
    job_title_reader = job_title_collector(rules)
    job_title_reader.send(None)
    fetch_data(target_site, job_monitor, job_title_reader)
    print(f"Finished filtering.\nEffective entries: {len(job_monitor.effective_entries)}\nIgnored entries: {job_monitor.ignored_titles}")
