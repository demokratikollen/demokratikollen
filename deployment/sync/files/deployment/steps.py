import os
import diff
from docker import Client
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
        os.path.join(base_dir, 'docker/bgtasks/demokratikollen/data/urls.txt')
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

def create_images(base_dir, logger, files_changed):
    cli = Client(base_url='unix://var/run/docker.sock')

    def create_image(name):
        docker_path = os.path.join(base_dir, 'docker/' + name)
        full_name = 'demokratikollen/' + name
        if p['prev_images'][name] in [full_name + ':two', '']:
            p['curr_images'][name] = full_name + ':one'
        else:
            p['curr_images'][name] = full_name + ':two'

        logger.info("Creating image: {0}".format(p['curr_images'][name]))
        response = [line for line in cli.build(path=docker_path, rm=True, tag=p['curr_images'][name])]

    p = params.get_params()

    # If files changed we need to create everything! the whole thing!
    if files_changed:
        create_image('postgres')
        create_image('mongo')
        create_image('bgtasks')

    #Regardless of changes of files we need a new webapp and nginx.
    create_image('webapp')
    create_image('nginx')

    params.set_params(p)

def remove_images(base_dir, logger, files_changed):

    def remove_image(name):
        if p['prev_images'][name]:
            logger.info("Removing image: {0}".format(p['prev_images'][name]))
            cli.remove_image(image=p['prev_images'][name])

    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    try:
        # Remove the extra containers if the files changed.
        if files_changed:
            remove_image('postgres')
            remove_image('mongo')
            remove_image('bgtasks')
    
        #remove webapp and nginx image if it exists
        remove_image('webapp')
        remove_image('nginx')
    except Exception as e:
        logger.error("Something went wrong with docker: {0} ".format(e))
        sys.exit(1)

def remove_containers(base_dir, logger, files_changed):

    def remove_container(name):
        if p['prev_containers'][name]:
            logger.info("Removing container: {0}".format(p['prev_containers'][name]))
            cli.remove_container(container=p['prev_containers'][name],v=True,force=True)

    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    try:
        # Remove the extra containers if the files changed.
        if files_changed:
            remove_container('postgres')
            remove_container('mongo')
            remove_container('bgtasks')
    
        #remove webapp and nginx image if it exists
        remove_container('webapp')
        remove_container('nginx')
    except Exception as e:
        logger.error("Something went wrong with docker: {0} ".format(e))
        sys.exit(1)

def create_containers(base_dir, logger, files_changed):

    def create_container(name):
        if p['prev_containers'][name] in [name + '_two', '']:
            p['curr_containers'][name] = name + '_one'
        else:
            p['curr_containers'][name] = name + '_two'

        image_name = p['curr_images'][name]

        logger.info("Creating container: {0}".format(p['curr_containers'][name]))
        if name == 'bgtasks':
            cli.create_container(image=image_name, name=p['curr_containers'][name], detach=True, volumes=['/data'])
        else:
            cli.create_container(image=image_name, name=p['curr_containers'][name], detach=True)

    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    try:
        if files_changed:
            create_container('postgres')
            create_container('mongo')
            create_container('bgtasks')

    #webapp and nginx
        create_container('webapp')
        create_container('nginx')
    except Exception as e:
        logger.error("Something went wrong with docker: {0} ".format(e))
        sys.exit(1)

    params.set_params(p)

def start_containers(base_dir, logger, files_changed):
    #start containers except nginx
    def start_container(name):
        logger.info("Starting container: {0}".format(name))

        if name == 'webapp':
            links = [(p['curr_containers']['postgres'],'postgres'), (p['curr_containers']['mongo'], 'mongo')]
            cli.start(container=p['curr_containers'][name], links=links)
        elif name == 'bgtasks':
            links = [(p['curr_containers']['postgres'],'postgres'), (p['curr_containers']['mongo'], 'mongo')]
            volumes = {'/home/wercker/data': {'bind': '/data', 'ro': False}}
            cli.start(container=p['curr_containers'][name], links=links, binds=volumes)
        else:
            cli.start(container=p['curr_containers'][name])

    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    try:
        if files_changed:
            start_container('postgres')
            start_container('mongo')
            start_container('bgtasks')

        start_container('webapp')
    except Exception as e:
        logger.error("Something went wrong with docker: {0} ".format(e))
        sys.exit(1)

def switch_nginx_servers(base_dir, logger):
    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    try:
        if p['prev_containers']['nginx']:
            logger.info("Stopping existing ngninx container: {0}".format(p['prev_containers']['nginx']))
            cli.stop(container=p['prev_containers']['nginx'])

        logger.info("Starting nginx container: {0}".format(p['curr_containers']['nginx']))
        link = [(p['curr_containers']['webapp'],'webapp')]
        port = {80: 81}
        cli.start(container=p['curr_containers']['nginx'], links=link, port_bindings=port)
    except Exception as e:
        logger.error("Something went wrong with docker: {0} ".format(e))
        sys.exit(1)

def populate_riksdagen(base_dir, logger):
    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    logger.info("Starting import_data on {0}".format(p['curr_containers']['bgtasks']))
    s = cli.execute(p['curr_containers']['bgtasks'], 'python import_data.py auto data/urls.txt /data --wipe', stream=True)

    for bytes in s:
        logger.info(bytes)

def populate_orm(base_dir, logger):
    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    logger.info("Starting populate_orm on {0}".format(p['curr_containers']['bgtasks']))

    try:
        s = cli.execute(p['curr_containers']['bgtasks'], 'python populate_orm.py', stream=True)

        for bytes in s:
            logger.info(bytes)
    except Exception as e:
        logger.error("Something went wrong during the orm population, continuing anyway: {0}".format(e))

def run_calculations(base_dir, logger):
    cli = Client(base_url='unix://var/run/docker.sock')
    p = params.get_params()

    commands = ['python compute_party_votes.py',
                'python calculations/party_covoting.py']
    for cmd in commands:
        logger.info("Starting {0} on {1}".format(cmd, p['curr_containers']['bgtasks']))

        try: 
            s = cli.execute(p['curr_containers']['bgtasks'], cmd, stream=True)

            for bytes in s:
                logger.info(bytes)
        except Exception as e:
            logger.error("Something went wrong during calculation {0}, continuing anyway: {1}".format(cmd, e))


def remove_orphaned_images_and_containers(base_dir, logger):
    raise NotImplemented

def post_deployment(base_dir, logger):
    
    # Save the current parameters.
    p = params.get_params()
    p['prev_images'] = dict(p['curr_images'])    # Object referencing fooled me, use dict to create a copy.
    p['prev_containers'] = dict(p['curr_containers'])
    params.set_params(p)

    #Copy this version of source files to the old_source files.
    current_src_path = os.path.join(base_dir, 'docker')
    prev_src_path = os.path.join(base_dir, 'docker_old')

    shutil.rmtree(prev_src_path)
    shutil.copytree(current_src_path, prev_src_path)



