ROOT = $(shell git rev-parse --show-toplevel)


lint:
	docker run --rm --volume $(ROOT):/src wellcome/flake8:65 --ignore=E501,W504
