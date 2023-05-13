from . import scraper, downloader


def mottit():
    scraper.main_scraper()
    downloader.main_download()
