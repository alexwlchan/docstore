import collections
import datetime
import os

from flask import Flask, jsonify, render_template, request, send_from_directory
import hyperlink

from docstore.files import get_documents


def create_app(root):
    app = Flask(__name__)

    @app.route('/')
    def list_documents():
        import time
        t0 = time.time()
        request_tags = set(request.args.getlist('tag'))
        documents = [
            doc
            for doc in get_documents(root)
            if request_tags.issubset(set(doc.tags))
        ]

        tag_tally = collections.Counter()
        for doc in documents:
            for t in doc.tags:
                tag_tally[t] += 1

        try:
            page = int(request.args['page'])
        except KeyError:
            page = 1

        print(time.time() - t0)

        return render_template(
            'index.html',
            documents=sorted(documents, key=lambda d: d.date_saved, reverse=True),
            request_tags=request_tags,
            request_url=hyperlink.DecodedURL.from_text(request.url),
            tag_tally=tag_tally,
            page=page,
        )

    @app.route('/thumbnails/<shard>/<filename>')
    def thumbnails(shard, filename):
        return send_from_directory(
            os.path.abspath(os.path.join(root, 'thumbnails', shard)), filename=filename
        )

    @app.route('/files/<shard>/<filename>')
    def files(shard, filename):
        return send_from_directory(
            os.path.abspath(os.path.join(root, 'files', shard)), filename=filename
        )

    @app.template_filter('attrib_tags')
    def attrib_tags(document):
        return [t for t in document.tags if t.startswith('by:')]

    @app.template_filter('display_tags')
    def display_tags(document):
        return sorted(
            t for t in document.tags if not t.startswith('by:')
        )

    @app.template_filter('add_tag')
    def add_tag(url, tag):
        return url.add('tag', tag).remove('page')

    @app.template_filter('hostname')
    def hostname(url):
        return hyperlink.URL.from_text(url).host

    @app.template_filter('pretty_date')
    def pretty_date(d):
        delta = datetime.datetime.now() - d
        if delta.seconds < 120:
            return 'just now'
        elif delta.seconds < 60 * 60:
            return f'{int(delta.seconds / 60)} minutes ago'
        elif d.date() == datetime.date.today():
            return 'earlier today'
        elif d.date() == datetime.date.today() - datetime.timedelta(days=1):
            return 'yesterday'
        elif delta.days < 7:
            return f'{delta.days} days ago'
        else:
            return d.strftime("%-d %b %Y")

    return app


def run_server(*, root, host, port, debug):
    app = create_app(root)
    app.run(host=host, port=port, debug=debug)
