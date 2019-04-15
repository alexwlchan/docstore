ROOT = $(shell git rev-parse --show-toplevel)


lint:
	docker run --rm --volume $(ROOT):/src wellcome/flake8:65 --ignore=E501,W504

build: requirements.txt
	docker build --target docstore --tag docstore .

test: test_requirements.txt
	docker build --target tests --tag docstore_test .
	make test-fast

test-fast:
	docker run --tty --volume $(ROOT):$(ROOT) --workdir $(ROOT)/src \
		--entrypoint "coverage" docstore_test run -m py.test tests
	docker run --tty --volume $(ROOT):$(ROOT) --workdir $(ROOT)/src \
		--entrypoint "coverage" docstore_test report

requirements.txt: requirements.in
	docker build --target pip_tools --tag docstore_piptools .
	docker run -v $(ROOT):/src --workdir /src docstore_piptools requirements.in

test_requirements.txt: requirements.txt test_requirements.in
	docker build --target pip_tools --tag docstore_piptools .
	docker run -v $(ROOT):/src --workdir /src docstore_piptools test_requirements.in
