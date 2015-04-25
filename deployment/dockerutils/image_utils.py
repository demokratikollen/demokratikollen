from docker import Client
cli = Client(base_url='unix://var/run/docker.sock')

def getImages():
	return cli.images()

def isImagePresent(image_name):
	image = cli.images(name=image_name)

	return len(image) > 0

def getImageID(image_name):
	image = cli.images(name=image_name)

	if len(image) == 0:
		return None

	return image[0]['Id']


def buildImageFromDockerfile(image_name, path_to_files):
	output = [line for line in cli.build(path=path_to_files, rm=True, forcerm=True, tag=image_name)]

	ID = getImageID(image_name)

	return ID, output

def removeUntaggedImages(force=False):
	images = cli.images()

	images_to_remove = []
	for image in images:
		if image['RepoTags'][0] == "<none>:<none>":
			images_to_remove.append(image['Id'])
	for image in images_to_remove:
		cli.remove_image(image=image, force=force)
	return images_to_remove

