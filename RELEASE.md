RELEASE_TYPE: patch

Internal refactoring.

Specifically, I'm using `humanize.naturaltime` from the [humanize module](https://pypi.org/project/humanize/), rather than hand-rolling my own code for printing date strings.  Less code for me to maintain!