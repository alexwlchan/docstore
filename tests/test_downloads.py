from email.message import Message

from docstore.downloads import guess_filename


def test_guess_filename_with_no_content_disposition() -> None:
    msg = Message()
    assert guess_filename("https://i.org/example.png", headers=msg) == "example.png"


def test_guess_filename_with_content_disposition() -> None:
    msg = Message()
    msg.add_header("Content-Disposition", "attachment", filename="MyExample.png")
    assert guess_filename("https://i.org/example.png", headers=msg) == "MyExample.png"


def test_guess_filename_with_content_disposition_but_no_filename() -> None:
    msg = Message()
    msg.add_header("Content-Disposition", "attachment")
    assert guess_filename("https://i.org/example.png", headers=msg) == "example.png"
