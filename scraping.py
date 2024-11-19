import io
import os
import urllib.request
from time import sleep
from urllib.parse import quote, unquote
from urllib.request import urlretrieve

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def get_soup_from_html(url, safe=True) -> BeautifulSoup:
    page_html = requests.get(url)
    while page_html.status_code != 200:
        print("page_html.status_code != 200 :", page_html.status_code)
        if not safe:
            return page_html.status_code
        sleep(30)
        page_html = requests.get(url)
    return BeautifulSoup(page_html.text, "html.parser")


def make_url_clickable(url: str):
    return quote(unquote(url), safe=':/?=')


def get_file_size(url):
    try:
        response = urllib.request.urlopen(url)
        size = response.headers.get('Content-Length')
        return int(size) if size else None
    except:
        return None


class download_progress_bar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_with_progress(url, output_path=None, save=True, debug=False):
    file_size = get_file_size(url)
    size_mb = f"{file_size / 1024 / 1024:.1f}MB" if file_size else "Unknown size"
    if debug:
        print(f"File size: {size_mb}")
    if save:
        with download_progress_bar(unit='B', unit_scale=True, miniters=1, desc=output_path) as t:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            urlretrieve(url, filename=output_path, reporthook=t.update_to)
        if os.path.exists(output_path):
            downloaded_size = os.path.getsize(output_path)
            if debug:
                print(f"\nDownload completed! Saved to: {output_path}", f"Downloaded size: {downloaded_size / 1024 / 1024:.1f}MB")
        else:
            print("\nError: File not found after download")
    else:
        response = requests.get(url, stream=True)
        file_size = int(response.headers.get('content-length', 0))
        size_mb = f"{file_size / 1024 / 1024:.1f}MB" if file_size else "Unknown size"
        if debug:
            print(f"File size: {size_mb}")
        file_content = io.BytesIO()
        print(unquote(url), url)
        with tqdm(total=file_size, unit='B', unit_scale=True, miniters=1, desc="Downloading") as t:
            for chunk in response.iter_content(chunk_size=8192):
                file_content.write(chunk)
                t.update(len(chunk))
        file_content.seek(0)
        if debug:
            downloaded_size = file_content.getbuffer().nbytes
            print(f"\nDownload completed! Downloaded size: {downloaded_size / 1024 / 1024:.1f}MB")
        return file_content

# class download_progress_bar(tqdm):
#     def update_to(self, b=1, bsize=1, tsize=None):
#         if tsize is not None:
#             self.total = tsize
#         self.update(b * bsize - self.n)
#
# def download_with_progress(url, output_path):
#     with download_progress_bar(unit='B', unit_scale=True,
#                            miniters=1, desc=output_path) as t:
#         urlretrieve(url, filename=output_path,
#                    reporthook=t.update_to)
