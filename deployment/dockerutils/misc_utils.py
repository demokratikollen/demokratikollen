import json


def decode_docker_log(stream):

	string = stream.decode("UTF-8")
	data = json.loads(string)

	return data