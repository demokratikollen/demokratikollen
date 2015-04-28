import os
import diff
from docker import Client
from dockerutils import container_utils, image_utils, misc_utils
import params
import shutil
import sys

cli = Client(base_url='unix://var/run/docker.sock')

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
    # We can always update all images to their new versions. 
    images_to_create = ['postgres', 'mongo','webapp','nginx']

    # if deploy_settings['deploy_extent'] in ['ALL', 'CALCULATIONS'] and deploy_settings['files_changed']:

    for image in images_to_create:
        try:
            create_image(image, deploy_settings)
        except Exception as e:
            deploy_settings['log'].error("Something went wrong with docker: {0} ".format(e))
            raise

def setup_containers_for_calculations(deploy_settings):
    deploy_settings['log'].info("Creating and starting temporary mongo and postgres containers.")
    cont = cli.create_container(image='demokratikollen/postgres:latest',name='postgres-temp')
    cli.start(cont['Id'])

    cont = cli.create_container(image='demokratikollen/mongo:latest', name='mongo-temp')
    cli.start(cont['Id'])

    deploy_settings['log'].info("Creating, starting and populating a temporary webapp container")
    webapp_dir = os.path.join(deploy_settings['base_dir'],'demokratikollen')
    data_dir = os.path.join(deploy_settings['base_dir'],'data')
    binds = {}
    binds[webapp_dir] = {'bind': '/mnt/demokratikollen', 'ro': False}
    binds[data_dir] = {'bind': '/data', 'ro': False}
    links  = {}
    links['postgres-temp'] = 'postgres'
    links['mongo-temp'] = 'mongo'
    cont = cli.create_container(image='demokratikollen/webapp:latest', 
                                name='webapp-temp', 
                                command='python /etc/webapp/loop.py', 
                                volumes='/mnt/demokratikollen')
    cli.start(cont['Id'],binds=binds, links=links)
    container_utils.run_command_in_container(cont['Id'], 'cp -r /mnt/demokratikollen/demokratikollen /apps')


def stop_and_remove_temp_containers(deploy_settings):
    deploy_settings['log'].info("Stopping and remove temporary containers.")
    cli.remove_container(container='postgres-temp', force=True, v=True)
    cli.remove_container(container='mongo-temp', force=True, v=True)
    cli.remove_container(container='webapp-temp', force=True, v=True)

def save_database_data(deploy_settings):

    data_dir = os.path.join(deploy_settings['base_dir'],'data/database_dumps')
    binds = {}
    binds[data_dir] = {'bind': '/data', 'ro': False}

    links  = {}
    links['postgres-temp'] = 'postgres'
    links['mongo-temp'] = 'mongo'

    deploy_settings['log'].info("Saving Postgres database.")
    cont = cli.create_container(image='demokratikollen/postgres:latest',
                                command='/bin/sh -c "while true; do sleep 1; done"',
                                volumes='/data')
    cli.start(cont['Id'], binds=binds, links=links)
    container_utils.run_command_in_container(cont['Id'],
        "/bin/bash -c 'pg_dump -h postgres -U demokratikollen -c demokratikollen | gzip > /data/demokratikollen_postgres_latest.gz'")
    cli.remove_container(cont['Id'], v=True, force=True)

    deploy_settings['log'].info("Saving mongo database.")
    cont = cli.create_container(image='demokratikollen/mongo:latest',
                                command='/bin/sh -c "while true; do sleep 1; done"',
                                volumes='/data')
    cli.start(cont['Id'], binds=binds, links=links)
    container_utils.run_command_in_container(cont['Id'],
        "mongodump --host mongo --out /data/demokratikollen_mongo_latest")
    container_utils.run_command_in_container(cont['Id'],
        "chown -R {0}:{0} /data".format(deploy_settings['userid']))
    cli.remove_container(cont['Id'], v=True, force=True)

def populate_riksdagen(deploy_settings):
    deploy_settings['log'].info("Starting import_data")
    container_utils.run_command_in_container('webapp-temp', "/bin/bash -c 'cd /apps/demokratikollen && python import_data.py auto data/urls.txt /data --wipe'", log=deploy_settings['log'])

def populate_orm(deploy_settings):
    deploy_settings['log'].info("Starting populate_orm")

    container_utils.run_command_in_container('webapp-temp', "python /apps/demokratikollen/populate_orm.py", log=deploy_settings['log'])

    for bytes in s:
        # look for erros?
        if 'Traceback' in str(bytes) or 'ERROR' in str(bytes):
            raise Exception
        deploy_settings['log'].info(bytes)

def run_calculations(deploy_settings):

    base_cmd_path = 'python /apps/demokratikollen/'
    commands = [base_cmd_path + 'compute_party_votes.py',
                base_cmd_path + 'calculations/party_covoting.py',
                base_cmd_path + 'calculations/sankey_data.py',
                base_cmd_path + 'calculations/election_data.py',
                base_cmd_path + 'calculations/search.py',
                base_cmd_path + 'calculations/cosigning.py',
                base_cmd_path + 'calculations/scb_best_party_gender.py',
                base_cmd_path + 'calculations/scb_best_party_education.py',
                base_cmd_path + 'calculations/scb_elections.py',
                base_cmd_path + 'calculations/scb_polls.py']

    for cmd in commands:
        deploy_settings['log'].info("Starting calculation {0}".format(cmd))
        container_utils.run_command_in_container('webapp-temp', cmd, log=deploy_settings['log'])


def stop_and_remove_current_containers(deploy_settings):
    
    containers_to_stop = ['nginx', 'webapp', 'mongo', 'postgres']

    for container in containers_to_stop:
        if container_utils.isContainerRunning(container):
            deploy_settings['log'].info("Stopping " + container)
            cli.stop(container)
        if container_utils.isContainerPresent(container):
            deploy_settings['log'].info("Removing " + container)
            cli.remove_container(container)

def create_and_start_data_containers(deploy_settings):

    containers_to_start = ['webapp', 'postgres', 'mongo']

    for container in containers_to_start:
        if container_utils.isContainerRunning(container+'-data') == False:
            cont = cli.create_container(image='demokratikollen/'+ container + ':latest',
                                        name=container+'-data',
                                        command='/bin/sh -c "while true; do sleep 1; done"')
            cli.start(cont['Id'])
            deploy_settings['log'].info("Creating and starting data container: {0}".format(container+'-data'))


def create_and_start_app_containers(deploy_settings):

    cont = cli.create_container(image='demokratikollen/postgres:latest', name='postgres')
    cli.start(cont['Id'], volumes_from='postgres-data')

    cont = cli.create_container(image='demokratikollen/mongo:latest', name='mongo')
    cli.start(cont['Id'], volumes_from='mongo-data')

    cont = cli.create_container(image='demokratikollen/webapp:latest', name='webapp')
    cli.start(cont['Id'],volumes_from='webapp-data',links={'postgres': 'postgres', 'mongo':'mongo'})

    cont = cli.create_container(image='demokratikollen/nginx:latest', name='nginx')
    cli.start(cont['Id'],volumes_from='webapp-data', links={'webapp': 'webapp'}, port_bindings={80:80})

def update_database_data(deploy_settings):
    data_dir = os.path.join(deploy_settings['base_dir'],'data/database_dumps')
    binds = {}
    binds[data_dir] = {'bind': '/data', 'ro': False}

    links  = {}
    links['postgres'] = 'postgres'
    links['mongo'] = 'mongo'

    deploy_settings['log'].info("Updating the Postgres database.")
    cont = cli.create_container(image='demokratikollen/postgres:latest',
                                command='/bin/sh -c "while true; do sleep 1; done"',
                                volumes='/data')
    cli.start(cont['Id'], binds=binds, links=links)
    container_utils.run_command_in_container(cont['Id'],
        "/bin/bash -c 'gunzip -c /data/demokratikollen_postgres_latest.gz | psql -h postgres -U demokratikollen demokratikollen'",
        deploy_settings['log'])
    cli.remove_container(cont['Id'], v=True, force=True)

    deploy_settings['log'].info("Updating the mongo database.")
    cont = cli.create_container(image='demokratikollen/mongo:latest',
                                command='/bin/sh -c "while true; do sleep 1; done"',
                                volumes='/data')
    cli.start(cont['Id'], binds=binds, links=links)
    container_utils.run_command_in_container(cont['Id'],
        "mongorestore --host mongo --drop /data/demokratikollen_mongo_latest",
        deploy_settings['log'])
    cli.remove_container(cont['Id'], v=True, force=True)    

def update_webapp_src(deploy_settings):

    web_src_dir = os.path.join(deploy_settings['base_dir'],'demokratikollen')
    binds = {}
    binds[web_src_dir] = {'bind': '/mnt/websrc', 'ro': True}

    cont = cli.create_container(image='demokratikollen/webapp:latest',
                        name='webapp-temp',
                        command='/bin/sh -c "while true; do sleep 1; done"',
                        volumes='/mnt/websrc')
    cli.start(cont['Id'], binds=binds, volumes_from='webapp-data')

    container_utils.run_command_in_container('webapp-temp', "bash -c 'rm -rf /apps/* && cp -r /mnt/websrc/demokratikollen /apps/'")
    cli.remove_container(cont['Id'], force=True, v=True)

def pre_deployment(deploy_settings):
    pass

def post_deployment(deploy_settings):
    deploy_settings['log'].info("Saving source for next deploy.")

    old_src = os.path.join(deploy_settings['base_dir'],'demokratikollen_old')
    new_src = os.path.join(deploy_settings['base_dir'],'demokratikollen')
    shutil.rmtree(old_src)
    shutil.move(new_src,old_src)

    deploy_settings['log'].info("Retagging images.")
    image_names = ['demokratikollen/nginx', 
                   'demokratikollen/mongo',
                   'demokratikollen/postgres',
                   'demokratikollen/webapp']
    for image_name in image_names:
        cli.tag(image=image_name, tag='current', repository=image_name, force=True)
    
    if deploy_settings['redo_calculations']:
        current_mongo_database_dump =  os.path.join(deploy_settings['base_dir'],'data/database_dumps/demokratikollen_mongo_current')
        latest_mongo_database_dump  =  os.path.join(deploy_settings['base_dir'],'data/database_dumps/demokratikollen_mongo_latest')
        current_postgres_database_dump =  os.path.join(deploy_settings['base_dir'],'data/database_dumps/demokratikollen_postgres_current.gz')
        latest_postgres_database_dump  =  os.path.join(deploy_settings['base_dir'],'data/database_dumps/demokratikollen_postgres_latest.gz')

        deploy_settings['log'].info("Saving latest database dumps")
        
        shutil.rmtree(current_mongo_database_dump)
        shutil.move(latest_mongo_database_dump, current_mongo_database_dump)

        os.remove(current_postgres_database_dump)
        shutil.move(latest_postgres_database_dump, current_postgres_database_dump)

def clean_up_after_error(deploy_settings):
    deploy_settings['log'].info("Removing current src")
    shutil.rmtree(os.path.join(deploy_settings['base_dir'],'demokratikollen'))
    deploy_settings['log'].info("Cleaning up untagged Images")
    image_utils.removeUntaggedImages(force=True)

def create_image(name,deploy_settings):
    cli = Client(base_url='unix://var/run/docker.sock')

    docker_path = os.path.join(deploy_settings['base_dir'], 'demokratikollen/deployment/docker/' + name)
    full_name = 'demokratikollen/' + name

    deploy_settings['log'].info("Creating image: {0}".format(name))
    for line in cli.build(path=docker_path, rm=True, tag=full_name):
        log_data = misc_utils.decode_docker_log(line)

        if "error" in log_data:
            deploy_settings['log'].error("Something went wrong with docker: {0}".format(log_data['error']))
            raise Exception
        else:
            deploy_settings['log'].info("Docker: {0}".format(log_data['stream'].strip()))

