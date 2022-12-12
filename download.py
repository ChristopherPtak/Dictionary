
import sys

import requests
import tqdm


CHUNK_SIZE = 1024


class DownloadError(Exception):

    def __init__(self, code, reason):
        self.code = code
        self.reason = reason

    def show(self, stream):
        stream.write(f'Download failed: {self.code} {self.reason}\n')


def download_latest_wiktionary():

    hostname = 'dumps.wikimedia.org'
    path = 'enwiktionary/latest/'
    filename = 'enwiktionary-latest-pages-articles.xml.bz2'

    url = f'https://{hostname}/{path}{filename}'
    print(f'Downloading from {url}')

    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise DownloadError(response.status_code, response.reason)

    filesize = int(response.headers.get('content-length'))

    with open(filename, 'wb') as dumpfile:
        with tqdm.tqdm(
            desc=filename,
            total=filesize,
            unit='B',
            unit_scale=True,
            unit_divisor=CHUNK_SIZE
        ) as progress:
            for data in response.iter_content(chunk_size=CHUNK_SIZE):
                written = dumpfile.write(data)
                progress.update(written)


if __name__ == '__main__':
    try:
        download_latest_wiktionary()
    except DownloadError as e:
        e.show(sys.stderr)

