import pickle 
import os


def get_params(base_dir='/home/wercker'):
    params_file = os.path.join(base_dir, 'docker_params')
    try:
        f = open(params_file,'rb')
        params = pickle.load(f)
        f.close()
    except:
        params = {
            'prev_images': {'webapp':"", 'mongo':"", 'postgres':"", 'bgtasks':"", 'nginx':""},
            'curr_images': {'webapp':"", 'mongo':"", 'postgres':"", 'bgtasks':"", 'nginx':""},
            'prev_containers': {'webapp':"", 'mongo':"", 'postgres':"", 'bgtasks':"", 'nginx':""},
            'curr_containers': {'webapp':"", 'mongo':"", 'postgres':"", 'bgtasks':"", 'nginx':""}
        }
    return params

def set_params(params, base_dir='/home/wercker'):
    params_file = os.path.join(base_dir, 'docker_params')

    with open(params_file, 'wb') as f:
        pickle.dump(params, f)