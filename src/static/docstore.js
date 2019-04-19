function addQueryParameter(name, value) {
  var url = new URL(window.location.href);
  url.searchParams.append(name, value);
  return url.href
}

function setQueryParameter(name, value) {
  var url = new URL(window.location.href);
  url.searchParams.set(name, value);
  return url.href
}

function deleteQueryParameter(name) {
  var url = new URL(window.location.href);
  url.searchParams.delete(name);
  return url.href
}

function addTagToUrl(value) {
  var url = new URL(window.location.href);
  existingTags = url.searchParams.getAll("tag");
  if (!existingTags.includes(value)) {
    return addQueryParameter("tag", value);
  } else {
    return url.href;
  }
}

function deleteTag(value) {
  var url = new URL(window.location.href);
  existingTags = url.searchParams.getAll("tag");
  if (existingTags.includes(value)) {
    url.searchParams.delete("tag");
    for (i = 0; i < existingTags.length; i++) {
      tag = existingTags[i];
      if (tag != value) {
        url.searchParams.append("tag", value);
      }
    }
  }

  return url.href
}
