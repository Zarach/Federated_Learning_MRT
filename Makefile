TAG ?= $(shell git describe --tags --always --dirty)
REGISTRY ?= registry.gitlab.com/team-ft/federated-learning

docker-build-server:
	docker build -t ${REGISTRY}/server:${TAG} -f Dockerfile.server . 

docker-build-client:
	docker build -t ${REGISTRY}/client:${TAG} -f Dockerfile.client . 

docker-build: docker-build-server docker-build-client

docker-push: docker-build
	docker push ${REGISTRY}/server:${TAG}
	docker push ${REGISTRY}/client:${TAG}