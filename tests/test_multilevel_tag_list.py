# -*- encoding: utf-8

import string

import bs4
import hyperlink
from hypothesis import given, HealthCheck, settings
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
              <li><a href="?tag=alfa:alfa">alfa</a> (0)</li>
            </ul>
          </li>
          <li>
            <span class="non-link-tag">bravo</span>
            <ul>
              <li><a href="?tag=bravo:alfa">alfa</a> (0)</li>
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
            <a href="?tag=alfa">alfa</a> (0)
            <ul>
              <li><a href="?tag=alfa:alfa">alfa</a> (0)</li>
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
            <a href="?tag=seasons">seasons</a> (3)
            <ul>
              <li><a href="?tag=seasons:autumn">autumn</a> (4)</li>
            </ul>
          </li>
          <li><a href="?tag=trees">trees</a> (2)</li>
        </ul>
        """
    ),
    (
        {"seasons": 3, "seasons:autumn": 4, "seasons:autumn:orange": 1, "trees": 2},
        """
        <ul>
          <li>
            <a href="?tag=seasons">seasons</a> (3)
            <ul>
              <li>
                <a href="?tag=seasons:autumn">autumn</a> (4)
                <ul>
                  <li><a href="?tag=seasons:autumn:orange">orange</a> (1)</li>
                </ul>
              </li>
            </ul>
          </li>
          <li><a href="?tag=trees">trees</a> (2)</li>
        </ul>
        """
    ),
    (
        {"seasons": 3, "seasons:autumn": 4, "seasons:winter": 2, "trees": 2},
        """
        <ul>
          <li>
            <a href="?tag=seasons">seasons</a> (3)
            <ul>
              <li><a href="?tag=seasons:autumn">autumn</a> (4)</li>
              <li><a href="?tag=seasons:winter">winter</a> (2)</li>
            </ul>
          </li>
          <li><a href="?tag=trees">trees</a> (2)</li>
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
                <a href="?tag=seasons:autumn">autumn</a> (4)
                <ul>
                  <li><a href="?tag=seasons:autumn:orange">orange</a> (1)</li>
                </ul>
              </li>
            </ul>
          </li>
          <li><a href="?tag=trees">trees</a> (2)</li>
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
                <a href="?tag=seasons:autumn">autumn</a> (4)
                <ul>
                  <li><a href="?tag=seasons:autumn:orange">orange</a> (1)</li>
                </ul>
              </li>
            </ul>
          </li>
          <li>
            <span class="non-link-tag">trees</span>
            <ul>
              <li><a href="?tag=trees:ash">ash</a> (2)</li>
              <li><a href="?tag=trees:oak">oak</a> (2)</li>
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
                      <li><a href="?tag=a:b:c:d">d</a> (4)</li>
                      <li><a href="?tag=a:b:c:e">e</a> (1)</li>
                    </ul>
                  </li>
                  <li>
                    <a href="?tag=a:b:f">f</a> (2)
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
                  <li><a href="?tag=trees:ash:branch">branch</a> (3)</li>
                  <li><a href="?tag=trees:ash:flower">flower</a> (4)</li>
                </ul>
              </li>
              <li><a href="?tag=trees:oak">oak</a> (2)</li>
            </ul>
          </li>
          <li>
            <span class="non-link-tag">unicorns</span>
            <ul>
              <li><a href="?tag=unicorns:horn">horn</a> (5)</li>
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
                <a href="?tag=trees:ash">ash</a> (7)
                <ul>
                  <li><a href="?tag=trees:ash:leaf">leaf</a> (3)</li>
                </ul>
              </li>
            </ul>
          </li>
          <li>
            <span class="non-link-tag">unicorns</span>
            <ul>
              <li><a href="?tag=unicorns:horn">horn</a> (5)</li>
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


def tag_strategy():   # pragma: no cover
    return lists(
        text(alphabet=string.ascii_lowercase, min_size=1, max_size=1),
        min_size=1).map(lambda tags: ":".join(tags))


@pytest.mark.skip("This test is really slow and mostly not interesting")
@settings(deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(dictionaries(tag_strategy(), integers()))
def test_can_render_tag_counter(tag_counter):  # pragma: no cover
    req_url = hyperlink.URL.from_text("http://localhost:1234/")

    html = render_tags(req_url=req_url, tag_counter=tag_counter)

    assert html.count("<ul>") == html.count("</ul>")
    assert html.count("<li>") == html.count("</li>")
    assert html.count("<a ") == html.count("</a>")
    assert html.count("<span ") == html.count("</span>")
