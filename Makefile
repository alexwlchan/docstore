ROOT = $(shell git rev-parse --show-toplevel)


lint:
	docker run --rm --volume $(ROOT):/src wellcome/flake8:65 --ignore=E501,W504

build: requirements.txt
	docker build --target=docstore --tag=docstore .

test: test_requirements.txt
	docker build --target=docstore_test --tag=docstore_test .
	docker run --tty --volume $(ROOT):$(ROOT) --workdir $(ROOT)/src docstore_test \
		coverage run -m py.test tests
	docker run --tty --volume $(ROOT):$(ROOT) --workdir $(ROOT)/src docstore_test \
		coverage report

requirements.txt: requirements.in
	docker build --target docstore_piptools -t docstore_piptools .
	docker run -v $(ROOT):/src --workdir /src docstore_piptools pip-compile

test_requirements.txt: requirements.txt test_requirements.in
	docker build --target docstore_piptools -t docstore_piptools .
	docker run -v $(ROOT):/src --workdir /src docstore_piptools pip-compile test_requirements.in