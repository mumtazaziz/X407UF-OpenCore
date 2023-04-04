import json
import os
import shutil
import urllib.request


def prepareOutput(outdir: str) -> None:
    shutil.rmtree(outdir, ignore_errors=True)
    os.mkdir(outdir)


def prepareCache(cachedir: str) -> None:
    if not os.path.exists(cachedir):
        os.mkdir(cachedir)
        return


def cleanupCache(cachedir: str) -> None:
    outdated_files: list[str] = getOutdatedFiles(os.listdir(cachedir))
    for outdated_file in outdated_files:
        os.unlink(os.path.join(cachedir, outdated_file))


def getOutdatedFiles(files: list[str]) -> list[str]:
    files.sort()
    files_for_deletion: list[str] = []
    prev_file: str | None = None
    for file in files:
        if prev_file is not None:
            a: list[str] = getFilenameComponents(prev_file)
            b: list[str] = getFilenameComponents(file)
            if a[0] == b[0] and a[1] < b[1]:
                files_for_deletion.append(prev_file)
        prev_file = file
    return files_for_deletion


def getFilenameComponents(filename: str) -> list[str]:
    for separator in ['-', '_']:
        if separator in filename:
            return filename.split(separator)
    return [filename]


def downloadLatestReleaseFromGitHub(repo: str, cachedir: str | None = None) -> str:
    data = json.load(urllib.request.urlopen(
        'https://api.github.com/repos/'+repo+'/releases/latest'))
    asset = next(
        (x for x in data['assets'] if 'RELEASE' in x['name']),
        data['assets'][0])
    filename: str = asset['name']
    if (cachedir is not None and os.path.exists(os.path.join(cachedir, filename))):
        print('Use cached download for '+filename)
        return os.path.join(cachedir, filename)
    download_url = asset['browser_download_url']
    print('Downloading ' + filename + ' from ' + repo)
    downloaded_path = urllib.request.urlretrieve(
        download_url,
        os.path.join(cachedir, filename)
        if cachedir is not None else None
    )[0]
    print('Downloaded ' + filename + ' as ' + downloaded_path)
    return downloaded_path
