from DockerImageBuilder import DockerImageBuilder

dib = DockerImageBuilder("docker/mongo", "mongo_test")
dib.build_image()
print(dib.output)