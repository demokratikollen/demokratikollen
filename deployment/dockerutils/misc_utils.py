import json
from docker import Client

cli = Client(base_url='unix://var/run/docker.sock')

def decode_docker_log(stream):

    string = stream.decode("UTF-8")
    data = json.loads(string)

    return data

def removeUnusedVolumes():
    sock_file = '/var/run/docker.sock'
    lib_dir = '/var/lib/docker'
    binds = {}
    binds[sock_file] = {'bind': sock_file, 'ro': False}
    binds[lib_dir] = {'bind': lib_dir, 'ro': False}
    cont = cli.create_container(image='martin/docker-cleanup-volumes', 
                                name='docker-cleanup', 
                                volumes=[sock_file, lib_dir])
    cli.start(cont['Id'], binds=binds)
    cli.remove_container(cont['Id'],force=True)