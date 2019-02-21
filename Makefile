ROOT = $(shell git rev-parse --show-toplevel)


lint:
	docker run --rm --volume $(ROOT):/src wellcome/flake8:65 --ignore=E501,W504

build:
	docker build --target=docstore --tag=docstore .

test:
	docker build --target=docstore_test --tag=docstore_test .
	docker run --tty --volume $(ROOT):$(ROOT) --workdir $(ROOT)/src docstore_test \
		coverage run -m py.test tests
	docker run --tty --volume $(ROOT):$(ROOT) --workdir $(ROOT)/src docstore_test \
		coverage report
