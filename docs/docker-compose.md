# Using Docker Compose to run docstore

I run lots of docstore instances, with different types of document in each instance.
For example, I have one instance for all my ebooks, and another for all my PDF manuals.

I use [Docker Compose](https://docs.docker.com/compose/) to define a set of options for each instance, and then I can always start an instance with the same settings.
You don't need Compose to run docstore, but I find it helpful.

Docker Compose is [installed separately](https://docs.docker.com/compose/install/) from Docker.

Once you have compose installed, create a file called `docker-compose.yml` with the following contents:

```yaml
version: "3.7"

services:
  manuals:
    image: "greengloves/docstore:v1.13.1"
    volumes:
    - /Users/alexwlchan/manuals:/documents
    ports:
      - "8072:8072"
    command: ["--title", "My household manuals"]
```

(Options such as `--title` are described in the [usage options](usage.md).)

Then, in the directory where you saved this file, run the following command:

```console
$ docker-compose up -d
```

This will start the docstore container in the background, and make it available at http://localhost:8072.

To stop the containers, run:

```console
$ docker-compose stop
```
