ROOT = $(shell git rev-parse --show-toplevel)


$(ROOT)/.docker/base: docker/base.Dockerfile
	docker build --tag docstore_base --file docker/base.Dockerfile .
	mkdir -p $(ROOT)/.docker
	touch $(ROOT)/.docker/base

$(ROOT)/.docker/tests: $(ROOT)/.docker/app test_requirements.txt
	docker build --tag docstore_tests --file docker/tests.Dockerfile .
	mkdir -p $(ROOT)/.docker
	touch $(ROOT)/.docker/tests

$(ROOT)/.docker/pip_tools: $(ROOT)/.docker/base
	docker build --tag docstore_pip_tools --file docker/pip_tools.Dockerfile .
	mkdir -p $(ROOT)/.docker
	touch $(ROOT)/.docker/pip_tools

deps = $(ROOT)/.docker/base docker/app.Dockerfile requirements.txt $(wildcard $(ROOT)/src/*)

$(ROOT)/.docker/app: $(deps)
	docker build --tag docstore --file docker/app.Dockerfile .
	mkdir -p $(ROOT)/.docker
	touch $(ROOT)/.docker/app


lint:
	docker run --rm --volume $(ROOT):/src wellcome/flake8:65 --ignore=E501,W504

build: $(ROOT)/.docker/app

test: $(ROOT)/.docker/tests test-fast

test-fast:
	docker run --tty \
		--volume $(ROOT):$(ROOT) \
		--env DOCKER=true \
		--workdir $(ROOT) \
		--entrypoint "coverage" docstore_tests run -m py.test -Werror tests
	docker run --tty --volume $(ROOT):$(ROOT) --workdir $(ROOT) \
		--entrypoint "coverage" docstore_tests report

requirements.txt: $(ROOT)/.docker/pip_tools requirements.in
	docker run -v $(ROOT):/src --workdir /src docstore_pip_tools requirements.in

test_requirements.txt: $(ROOT)/.docker/pip_tools requirements.txt test_requirements.in
	docker run -v $(ROOT):/src --workdir /src docstore_pip_tools test_requirements.in

check_release_file:
	python tooling/autorelease.py check_release_file

autorelease:
	python tooling/autorelease.py release
