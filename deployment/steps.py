import os
import diff
from docker import Client
from dockerutils import container_utils, image_utils
import params
import shutil
import sys

def verify_changes(base_dir, logger):
    changed = []

    diff_rd = diff.riksdagen(base_dir)
    if diff_rd:
        changed.append('riksdagen')
    logger.info("Riksdagen dir diff status: {0}".format(diff_rd))

    diff_rf = diff.remote_files(
        os.path.join(base_dir, 'data/download') ,
        os.path.join(base_dir, 'demokratikollen/demokratikollen/data/urls.txt')
        )
    if diff_rf:
        changed.append('riksdagen_remote')
    logger.info("Riksdagen remote files diff status: {0}".format(diff_rf))

    diff_c = diff.calculations(base_dir)
    if diff_c:
        changed.append('calculations')
    logger.info("Calculations diff status: {0}".format(diff_c))

    diff_db = diff.dbstructure(base_dir)
    if diff_db:
        changed.append('db_structure')
    logger.info("DB Strutucre diff status: {0}".format(diff_db))

    return changed

def create_images(deploy_settings):
    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    images_to_create = []

    # If files changed we need to create everything! the whole thing!
    if deploy_settings['deploy_extent'] in ['ALL', 'CALCULATIONS'] and deploy_settings['files_changed']:
        images_to_create += ['postgres', 'mongo', 'bgtasks']

    #Regardless of changes of files we need a new webapp and nginx.
    images_to_create += ['webapp', 'nginx']

    for image in images_to_create:
        try:
            create_image(image, deploy_settings)
        except Exception as e:
            deploy_settings['log'].error("Something went wrong with docker: {0} ".format(e))
            raise

def remove_images(deploy_settings):
    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    images_to_remove = []

    # Remove the extra containers if the files changed.
    if deploy_settings['deploy_extent'] in ['ALL', 'CALCULATIONS'] and deploy_settings['files_changed']:
        images_to_remove += ['postgres', 'mongo','bgtasks']
    #remove webapp and nginx image if it exists
    images_to_remove += ['webapp', 'nginx']

    for image in images_to_remove:
        try:
            remove_image(image,deploy_settings)
        except Exception as e:
            deploy_settings['log'].error("Something went wrong with docker, continuing anyway: {0} ".format(e))

def remove_containers(deploy_settings):
    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    containers_to_remove = []

    if deploy_settings['deploy_extent'] in ['ALL', 'CALCULATIONS'] and deploy_settings['files_changed']:
        containers_to_remove += ['postgres', 'mongo', 'bgtasks']

    containers_to_remove += ['webapp', 'nginx']

    for container in containers_to_remove:
        try:
            remove_container(container,deploy_settings)
        except Exception as e:
            deploy_settings['log'].error("Something went wrong with docker, continuing anyway: {0} ".format(e))


def create_containers(deploy_settings):
    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    containers_to_create = []

    # If files changed we need to create everything! the whole thing!
    if deploy_settings['deploy_extent'] in ['ALL', 'CALCULATIONS'] and deploy_settings['files_changed']:
        containers_to_create += ['postgres', 'mongo', 'bgtasks']

    #Regardless of changes of files we need a new webapp and nginx.
    containers_to_create += ['webapp', 'nginx']

    for container in containers_to_create:
        try:
            create_container(container,deploy_settings)
        except Exception as e:
            deploy_settings['log'].error("Something went wrong with docker: {0} ".format(e))
            raise

def start_containers(deploy_settings):
    #start containers except nginx

    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    containers_to_start = []

    # If files changed we need to create everything! the whole thing!
    if deploy_settings['deploy_extent'] in ['ALL', 'CALCULATIONS'] and deploy_settings['files_changed']:
        containers_to_start += ['postgres', 'mongo', 'bgtasks']

    #Regardless of changes of files we need a new webapp and nginx.
    containers_to_start += ['webapp', 'nginx']

    for container in containers_to_start:
        try:
            start_container(container,deploy_settings)
        except Exception as e:
            deploy_settings['log'].error("Something went wrong with docker: {0} ".format(e))
            raise

def switch_nginx_servers(deploy_settings):
    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    try:
        if p['prev_containers']['nginx']:
            deploy_settings['log'].info("Stopping existing ngninx container: {0}".format(p['prev_containers']['nginx']))
            cli.stop(container=p['prev_containers']['nginx'])

        deploy_settings['log'].info("Starting nginx container: {0}".format(p['curr_containers']['nginx']))
        link = [(p['curr_containers']['webapp'],'webapp')]
        port = {80: 80}
        cli.start(container=p['curr_containers']['nginx'], links=link, port_bindings=port)
    except Exception as e:
        deploy_settings['log'].error("Something went wrong with docker: {0} ".format(e))
        raise

def populate_riksdagen(deploy_settings):
    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    deploy_settings['log'].info("Starting import_data on {0}".format(p['curr_containers']['bgtasks']))
    s = cli.execute(p['curr_containers']['bgtasks'], 'python import_data.py auto data/urls.txt /data --wipe', stream=True)

    for bytes in s:
        # look for erros?
        if 'Traceback' in str(bytes) or 'ERROR' in str(bytes):
            raise Exception
        deploy_settings['log'].info(bytes)

def populate_orm(deploy_settings):
    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    deploy_settings['log'].info("Starting populate_orm on {0}".format(p['curr_containers']['bgtasks']))

    s = cli.execute(p['curr_containers']['bgtasks'], 'python populate_orm.py', stream=True)

    for bytes in s:
        # look for erros?
        if 'Traceback' in str(bytes) or 'ERROR' in str(bytes):
            raise Exception
        deploy_settings['log'].info(bytes)

def run_calculations(deploy_settings):
    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    commands = ['python compute_party_votes.py',
                'python calculations/party_covoting.py',
                'python calculations/sankey_data.py',
                'python calculations/election_data.py',
                'python calculations/search.py',
                'python calculations/cosigning.py',
                'python calculations/scb_best_party_gender.py',
                'python calculations/scb_best_party_education.py',
                'python calculations/scb_elections.py',
                'python calculations/scb_polls.py']
    for cmd in commands:
        deploy_settings['log'].info("Starting {0} on {1}".format(cmd, p['curr_containers']['bgtasks']))

        s = cli.execute(p['curr_containers']['bgtasks'], cmd, stream=True)

        for bytes in s:
            # look for erros?
            if 'Traceback' in str(bytes) or 'ERROR' in str(bytes):
                raise Exception
            deploy_settings['log'].info(bytes)


def remove_orphaned_images_and_containers(base_dir, logger):
    raise NotImplemented

def remove_current_images_and_containers(deploy_settings):
    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    for container, name in p['curr_containers'].items():
        if name != p['prev_containers'][container]:
            try:
                remove_container(container,deploy_settings)
            except Exception as e:
                deploy_settings['log'].error("Something went wrong with docker, continuing anyway: {0}".format(e))

    for image, name in p['curr_images'].items():
        if name != p['prev_images'][image]:
            try:
                remove_image(image, deploy_settings)
            except Exception as e:
                deploy_settings['log'].error("Something went wrong with docker, continuing anyway: {0}".format(e))

def pre_deployment(deploy_settings):
    pass

def post_deployment(deploy_settings):

    deploy_settings['log'].info("Saving parameters and removing lockfile")

    # Save the current parameters.
    p = params.get_params()
    p['prev_images'] = dict(p['curr_images'])    # Object referencing fooled me, use dict to create a copy.
    p['prev_containers'] = dict(p['curr_containers'])
    params.set_params(p)

    #Copy this version of source files to the old_source files.
    current_src_path = os.path.join(deploy_settings['base_dir'], 'docker')
    prev_src_path = os.path.join(deploy_settings['base_dir'], 'docker_old')

    shutil.rmtree(prev_src_path)
    shutil.copytree(current_src_path, prev_src_path)

def create_container(name, deploy_settings):
    p = params.get_params()
    cli = Client(base_url='unix://var/run/docker.sock')

    if p['prev_containers'][name] in [name + '_two', '']:
        p['curr_containers'][name] = name + '_one'
    else:
        p['curr_containers'][name] = name + '_two'

    params.set_params(p)
    image_name = p['curr_images'][name]

    deploy_settings['log'].info("Creating container: {0}".format(p['curr_containers'][name]))
    if name == 'bgtasks':
        cli.create_container(image=image_name, name=p['curr_containers'][name], detach=True, volumes=['/data'])
    else:
        cli.create_container(image=image_name, name=p['curr_containers'][name], detach=True)

def start_container(name, deploy_settings):
    p = params.get_params()
    cli = Client(base_url='unix://var/run/docker.sock')

    deploy_settings['log'].info("Starting container: {0}".format(name))

    if name == 'webapp':
        links = [(p['curr_containers']['postgres'],'postgres'), (p['curr_containers']['mongo'], 'mongo')]
        cli.start(container=p['curr_containers'][name], links=links)
    elif name == 'bgtasks':
        links = [(p['curr_containers']['postgres'],'postgres'), (p['curr_containers']['mongo'], 'mongo')]
        volumes = {'/home/wercker/data': {'bind': '/data', 'ro': False}}
        cli.start(container=p['curr_containers'][name], links=links, binds=volumes)
    else:
        cli.start(container=p['curr_containers'][name])


def remove_container(name, deploy_settings):
    p = params.get_params()
    cli = Client(base_url='unix://var/run/docker.sock')

    if p['prev_containers'][name]:
        deploy_settings['log'].info("Removing container: {0}".format(p['prev_containers'][name]))
        cli.remove_container(container=p['prev_containers'][name],v=True,force=True)


def remove_image(name, deploy_settings):
    p = params.get_params()
    cli = Client(base_url='unix://var/run/docker.sock')

    if p['prev_images'][name]:
        deploy_settings['log'].info("Removing image: {0}".format(p['prev_images'][name]))
        cli.remove_image(image=p['prev_images'][name])

def create_image(name,deploy_settings):
    p = params.get_params()
    cli = Client(base_url='unix://var/run/docker.sock')

    docker_path = os.path.join(deploy_settings['base_dir'], 'docker/' + name)
    full_name = 'demokratikollen/' + name
    if p['prev_images'][name] in [full_name + ':two', '']:
        p['curr_images'][name] = full_name + ':one'
    else:
        p['curr_images'][name] = full_name + ':two'

    params.set_params(p)

    deploy_settings['log'].info("Creating image: {0}".format(p['curr_images'][name]))
    response = [line for line in cli.build(path=docker_path, rm=True, tag=p['curr_images'][name])]
