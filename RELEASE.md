RELEASE_TYPE: patch

This fixes a small bug in the tag list if you had a heavily nested hierarchy of tags, where the hierarchy wouldn't de-nest correctly.

For example, you could see the following incorrect nesting where `delta` is indented too far:

    - alfa
      - alfa:bravo
        - alfa:bravo:charlie
      - delta

It also cleans up the display of tags, so rather than the above you'd see:

    - alfa
      - bravo
        - charlie
    - delta

This indicates four tags: `alfa`, `alfa:bravo`, `alfa:bravo:charlie` and `delta`, but with less repetition.

This new version is based on code [from Dreamwidth](https://github.com/dreamwidth/dw-free/blob/6ec1e146d3c464e506a77913f0abf0d51a944f95/styles/core2.s2#L4126).