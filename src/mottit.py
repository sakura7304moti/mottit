from . import scraper, downloader, sqlite


def mottit():
    scraper.main_scraper()
    downloader.main_download()
    sqlite.update_all()
