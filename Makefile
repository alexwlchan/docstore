ROOT = $(shell git rev-parse --show-toplevel)


$(ROOT)/.docker/base: docker/base.Dockerfile
	docker build --tag docstore_base --file docker/base.Dockerfile .
	mkdir -p $(ROOT)/.docker
	touch $(ROOT)/.docker/base

$(ROOT)/.docker/tests: build test_requirements.txt
	docker build --tag docstore_tests --file docker/tests.Dockerfile .
	mkdir -p $(ROOT)/.docker
	touch $(ROOT)/.docker/tests

lint:
	docker run --rm --volume $(ROOT):/src wellcome/flake8:65 --ignore=E501,W504

build: $(ROOT)/.docker/base
	docker build --tag docstore --file docker/app.Dockerfile .

test: $(ROOT)/.docker/tests test-fast

test-fast:
	docker run --tty \
		--volume $(ROOT):$(ROOT) \
		--env DOCKER=true \
		--workdir $(ROOT) \
		--entrypoint "coverage" docstore_tests run -m py.test --durations=5 tests
	docker run --tty --volume $(ROOT):$(ROOT) --workdir $(ROOT) \
		--entrypoint "coverage" docstore_tests report

requirements.txt: requirements.in
	docker build --tag docstore_pip_tools --file docker/pip_tools.Dockerfile .
	docker run -v $(ROOT):/src --workdir /src docstore_pip_tools requirements.in

test_requirements.txt: test_requirements.in requirements.txt
	docker build --tag docstore_pip_tools --file docker/pip_tools.Dockerfile .
	docker run -v $(ROOT):/src --workdir /src docstore_pip_tools test_requirements.in

check_release_file:
	python3 tooling/autorelease.py check_release_file

autorelease:
	python3 tooling/autorelease.py release
