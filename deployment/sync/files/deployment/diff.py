import os
import urllib.request
import urllib.parse
import filecmp

def riksdagen(base_dir):
    riksdagen_diff = filecmp.dircmp(
        os.path.join(base_dir, 'docker/bgtasks/demokratikollen/data') ,
        os.path.join(base_dir, 'docker_old/bgtasks/demokratikollen/data')
        )

    return riksdagen_diff.left_list != riksdagen_diff.right_list or len(riksdagen_diff.diff_files) > 0

def calculations(base_dir):
    calc_diff = filecmp.dircmp(
        os.path.join(base_dir, 'docker/bgtasks/demokratikollen/calculations') ,
        os.path.join(base_dir, 'docker_old/bgtasks/demokratikollen/calculations') )

    return calc_diff.left_list != calc_diff.right_list or len(calc_diff.diff_files) > 0

def dbstructure(base_dir):

    try:
        diff = filecmp.cmp(
            os.path.join(base_dir, 'docker/bgtasks/demokratikollen/core/db_structure.py') ,
            os.path.join(base_dir, 'docker_old/bgtasks/demokratikollen/core/db_structure.py')
                )

    except FileNotFoundError as e:
        return True
    return not diff


def remote_files(data_dir, urls_file): 
    with open(urls_file, encoding='utf-8') as f:
        urls = f.readlines()

    for url in urls:
        url = url.strip()
        urlparts = urllib.parse.urlparse(url)
        filename = os.path.split(urlparts.path)[1]
        out_path = os.path.abspath(os.path.join(data_dir, filename))

        local_size = os.path.getsize(out_path)
        response = urllib.request.urlopen(url)
        remote_size = int(response.getheader('Content-Length'))
        if local_size != remote_size:
            return True

    return False