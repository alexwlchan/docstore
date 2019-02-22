// https://stackoverflow.com/a/41542008/1558022
function gotoTag(tagName) {
  var searchParams = new URLSearchParams(window.location.search);
  if (!searchParams.getAll("tag").includes(tagName)) {
    searchParams.append("tag", tagName);
    window.location = window.location.pathname + '?' + searchParams.toString();
  }
}

function removeTag(tagName) {
  var searchParams = new URLSearchParams(window.location.search);
  if (searchParams.getAll("tag").includes(tagName)) {
    existing = searchParams.getAll("tag");
    searchParams.delete("tag");
    for (i = 0; i < existing.length; i++) {
      var t = existing[i];
      if (t != tagName) {
        searchParams.append("tag", t);
      }
    }
    window.location = window.location.pathname + '?' + searchParams.toString();
  }
}

function setSortOrder(sortOrder) {
  var searchParams = new URLSearchParams(window.location.search);
  searchParams.delete("sort");
  searchParams.append("sort", sortOrder);
  window.location = window.location.pathname + '?' + searchParams.toString();
}

function setPageNumber(pageNumber) {
  var searchParams = new URLSearchParams(window.location.search);
  searchParams.delete("page");

  if (pageNumber != 1) {
    searchParams.append("page", pageNumber);
  }

  window.location = window.location.pathname + '?' + searchParams.toString();
}
