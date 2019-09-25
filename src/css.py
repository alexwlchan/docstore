# -*- encoding: utf-8

import pathlib

import scss
from scss.namespace import Namespace
from scss.types import Color


def compile_css(accent_color):
    src_root = pathlib.Path(__file__).parent
    static_dir = src_root / "static"

    namespace = Namespace()
    namespace.set_variable("$accent_color", Color.from_hex(accent_color))
    css = scss.Compiler(
        root=src_root / "assets",
        namespace=namespace).compile("style.scss")

    css_path = static_dir / "style.css"
    css_path.write_text(css)
