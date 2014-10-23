all:
	docker build -t dosek-base dosek-base

run:
	docker run --name dosek-base -d dosek-base

ssh:
	ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
		dosek@$$(docker inspect --format "{{ .NetworkSettings.IPAddress }}" dosek-base)
