function setSortOrder(sortOrder) {
  var searchParams = new URLSearchParams(window.location.search);
  searchParams.delete("sort");
  searchParams.append("sort", sortOrder);
  window.location = window.location.pathname + '?' + searchParams.toString();
}

function setViewOption(viewOption) {
  var searchParams = new URLSearchParams(window.location.search);
  searchParams.delete("view");
  searchParams.append("view", viewOption);

  window.location = window.location.pathname + '?' + searchParams.toString();
}

