ROOT = $(shell git rev-parse --show-toplevel)


docker-base:
	docker build --tag docstore_base --file docker/base.Dockerfile .

docker-tests: docker-app
	docker build --tag docstore_tests --file docker/tests.Dockerfile .

docker-pip_tools: docker-base
	docker build --tag docstore_pip_tools --file docker/pip_tools.Dockerfile .

docker-app: docker-base
	docker build --tag docstore --file docker/app.Dockerfile .


lint:
	docker run --rm --volume $(ROOT):/src wellcome/flake8:65 --ignore=E501,W504

build: docker-app

test: docker-tests test-fast

test-fast:
	docker run --tty --volume $(ROOT):$(ROOT) --workdir $(ROOT) \
		--entrypoint "coverage" docstore_tests run -m py.test tests
	docker run --tty --volume $(ROOT):$(ROOT) --workdir $(ROOT) \
		--entrypoint "coverage" docstore_tests report

requirements.txt: docker-pip_tools requirements.in
	docker run -v $(ROOT):/src --workdir /src docstore_piptools requirements.in

test_requirements.txt: docker-pip_tools requirements.txt test_requirements.in
	docker run -v $(ROOT):/src --workdir /src docstore_piptools test_requirements.in

check_release_file:
	python .travis/autorelease.py check_release_file

autorelease:
	python .travis/autorelease.py release
