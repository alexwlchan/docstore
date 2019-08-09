# -*- encoding: utf-8

import string

import bs4
import hyperlink
from hypothesis import given, settings
from hypothesis.strategies import dictionaries, integers, lists, text
import pytest

from multilevel_tag_list import render_tags


def test_empty_tags_is_empty_string():
    req_url = hyperlink.URL.from_text("http://localhost:1234/")
    assert render_tags(tag_counter={}, req_url=req_url) == ""


@pytest.mark.parametrize("tag_counter, expected_html", [
    (
        {"alfa:alfa": 0, "bravo:alfa": 0},
        """
        <ul>
          <li>
            <span class="non-link-tag">alfa</span>
            <ul>
              <li><a href="?tag=alfa:alfa">alfa (0)</a></li>
            </ul>
          </li>
          <li>
            <span class="non-link-tag">bravo</span>
            <ul>
              <li><a href="?tag=bravo:alfa">alfa (0)</a></li>
            </ul>
          </li>
        </ul>
        """
    ),
    (
        {"alfa": 0, "alfa:alfa": 0},
        """
        <ul>
          <li>
            <a href="?tag=alfa">alfa (0)</a>
            <ul>
              <li><a href="?tag=alfa:alfa">alfa (0)</a></li>
            </ul>
          </li>
        </ul>
        """
    ),
    (
        {"seasons": 3, "seasons:autumn": 4, "trees": 2},
        """
        <ul>
          <li>
            <a href="?tag=seasons">seasons (3)</a>
            <ul>
              <li><a href="?tag=seasons:autumn">autumn (4)</a></li>
            </ul>
          </li>
          <li><a href="?tag=trees">trees (2)</a></li>
        </ul>
        """
    ),
    (
        {"seasons": 3, "seasons:autumn": 4, "seasons:autumn:orange": 1, "trees": 2},
        """
        <ul>
          <li>
            <a href="?tag=seasons">seasons (3)</a>
            <ul>
              <li>
                <a href="?tag=seasons:autumn">autumn (4)</a>
                <ul>
                  <li><a href="?tag=seasons:autumn:orange">orange (1)</a></li>
                </ul>
              </li>
            </ul>
          </li>
          <li><a href="?tag=trees">trees (2)</a></li>
        </ul>
        """
    ),
    (
        {"seasons": 3, "seasons:autumn": 4, "seasons:winter": 2, "trees": 2},
        """
        <ul>
          <li>
            <a href="?tag=seasons">seasons (3)</a>
            <ul>
              <li><a href="?tag=seasons:autumn">autumn (4)</a></li>
              <li><a href="?tag=seasons:winter">winter (2)</a></li>
            </ul>
          </li>
          <li><a href="?tag=trees">trees (2)</a></li>
        </ul>
        """
    ),
    (
        {
            "seasons:autumn": 4,
            "seasons:autumn:orange": 1,
            "trees": 2},
        """
        <ul>
          <li>
            <span class="non-link-tag">seasons</span>
            <ul>
              <li>
                <a href="?tag=seasons:autumn">autumn (4)</a>
                <ul>
                  <li><a href="?tag=seasons:autumn:orange">orange (1)</a></li>
                </ul>
              </li>
            </ul>
          </li>
          <li><a href="?tag=trees">trees (2)</a></li>
        </ul>
        """
    ),
    (
        {
            "seasons:autumn": 4,
            "seasons:autumn:orange": 1,
            "trees:ash": 2,
            "trees:oak": 2,
        },
        """
        <ul>
          <li>
            <span class="non-link-tag">seasons</span>
            <ul>
              <li>
                <a href="?tag=seasons:autumn">autumn (4)</a>
                <ul>
                  <li><a href="?tag=seasons:autumn:orange">orange (1)</a></li>
                </ul>
              </li>
            </ul>
          </li>
          <li>
            <span class="non-link-tag">trees</span>
            <ul>
              <li><a href="?tag=trees:ash">ash (2)</a></li>
              <li><a href="?tag=trees:oak">oak (2)</a></li>
            </ul>
          </li>
        </ul>
        """
    ),
    (
        {
            "a:b:c:d": 4,
            "a:b:c:e": 1,
            "a:b:f": 2,
        },
        """
        <ul>
          <li>
            <span class="non-link-tag">a</span>
            <ul>
              <li>
                <span class="non-link-tag">b</span>
                <ul>
                  <li>
                    <span class="non-link-tag">c</span>
                    <ul>
                      <li><a href="?tag=a:b:c:d">d (4)</a></li>
                      <li><a href="?tag=a:b:c:e">e (1)</a></li>
                    </ul>
                  </li>
                  <li>
                    <a href="?tag=a:b:f">f (2)</a>
                  </li>
                </ul>
              </li>
            </ul>
          </li>
        </ul>
        """
    ),
    (
        {
            "trees:ash:branch": 3,
            "trees:ash:flower": 4,
            "trees:oak": 2,
            "unicorns:horn": 5,
        },
        """
        <ul>
          <li>
            <span class="non-link-tag">trees</span>
            <ul>
              <li>
                <span class="non-link-tag">ash</span>
                <ul>
                  <li><a href="?tag=trees:ash:branch">branch (3)</a></li>
                  <li><a href="?tag=trees:ash:flower">flower (4)</a></li>
                </ul>
              </li>
              <li><a href="?tag=trees:oak">oak (2)</a></li>
            </ul>
          </li>
          <li>
            <span class="non-link-tag">unicorns</span>
            <ul>
              <li><a href="?tag=unicorns:horn">horn (5)</a></li>
            </ul>
          </li>
        </ul>
        """
    ),
    (
        {
            "trees:ash": 7,
            "trees:ash:leaf": 3,
            "unicorns:horn": 5,
        },
        """
        <ul>
          <li>
            <span class="non-link-tag">trees</span>
            <ul>
              <li>
                <a href="?tag=trees:ash">ash (7)</a>
                <ul>
                  <li><a href="?tag=trees:ash:leaf">leaf (3)</a></li>
                </ul>
              </li>
            </ul>
          </li>
          <li>
            <span class="non-link-tag">unicorns</span>
            <ul>
              <li><a href="?tag=unicorns:horn">horn (5)</a></li>
            </ul>
          </li>
        </ul>
        """
    ),
])
def test_renders_expected_html(tag_counter, expected_html):
    req_url = hyperlink.URL.from_text("http://localhost:1234/")

    actual_html = render_tags(req_url=req_url, tag_counter=tag_counter)

    actual_soup = bs4.BeautifulSoup(actual_html, "html.parser")
    expected_soup = bs4.BeautifulSoup(expected_html, "html.parser")

    assert (
        actual_soup.prettify(formatter="minimal").strip() ==
        expected_soup.prettify(formatter="minimal").strip()
    )


def tag_strategy():
    return lists(
        text(alphabet=string.ascii_lowercase, min_size=1, max_size=1),
        min_size=1).map(lambda tags: ":".join(tags))


@settings(deadline=None)
@given(dictionaries(tag_strategy(), integers()))
def test_can_render_tag_counter(tag_counter):
    req_url = hyperlink.URL.from_text("http://localhost:1234/")

    html = render_tags(req_url=req_url, tag_counter=tag_counter)

    assert html.count("<ul>") == html.count("</ul>")
    assert html.count("<li>") == html.count("</li>")
    assert html.count("<a ") == html.count("</a>")
    assert html.count("<span ") == html.count("</span>")
