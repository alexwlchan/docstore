RELEASE_TYPE: minor

This is a major refactor of the viewer.  Everything now uses CSS Grid (inspired by a CodePen [by Olivia Ng](https://codepen.io/oliviale/pen/WqwOzv)) and has a more consistent layout.  The underlying code is much simpler, yay.

The new design also works much better on smaller screens.

I've removed the buttons for changing the sort order because I wasn't using them.  The old URL query parameters will still work, but I'll probably delete them later.
