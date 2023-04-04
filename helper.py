import json
import os
import urllib.request


def prepareCache(cachedir='cache'):
    if not os.path.exists(cachedir):
        os.mkdir(cachedir)
        return
    outdated_files = getOutdatedFiles(os.listdir(cachedir))
    for outdated_file in outdated_files:
        os.unlink(os.path.join(cachedir, outdated_file))


def getOutdatedFiles(files: list[str]) -> list[str]:
    files.sort()
    files_for_deletion: list[str] = []
    prev_file = None
    for file in files:
        if prev_file is not None:
            a = getFilenameComponents(prev_file)
            b = getFilenameComponents(file)
            if a[0] == b[0] and a[1] < b[1]:
                files_for_deletion.append(prev_file)
        prev_file = file
    return files_for_deletion


def getFilenameComponents(filename: str):
    for separator in ['-', '_']:
        if separator in filename:
            return filename.split(separator)


def downloadLatestReleaseFromGitHub(repo: str, cachedir: str = None) -> str:
    data = json.load(urllib.request.urlopen(
        'https://api.github.com/repos/'+repo+'/releases/latest'))
    asset = next(
        (x for x in data['assets'] if 'RELEASE' in x['name']),
        data['assets'][0])
    filename = asset['name']
    downloaded_path = os.path.join(cachedir, filename)
    if (cachedir is not None and os.path.exists(downloaded_path)):
        print('Use cached download for '+filename)
        return str(downloaded_path)
    download_url = asset['browser_download_url']
    print('Downloading ' + filename + ' from ' + repo)
    downloaded_path = urllib.request.urlretrieve(
        download_url,
        os.path.join(cachedir, filename)
        if cachedir is not None else None
    )[0]
    print('Downloaded ' + filename + ' as ' + downloaded_path)
    return downloaded_path
