import requests
from pathlib import Path

def download_to_local(url, outpath, parent_mkdir=True):

    if not isinstance(outpath, Path):
        raise ValueError("Outpath must be a valid pathlib. Path object")

    if parent_mkdir:
        outpath.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    # Writing raw binary bytes to local files
    outpath.write_bytes(response.content)
    return True    