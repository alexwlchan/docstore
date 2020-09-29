from docstore.tint_colors import choose_tint_color, get_colors_from


def test_get_colors_from_small_image():
    result = get_colors_from("tests/files/cluster_segment.png")
    assert result == [
        (0, 154, 142),
        (0, 128, 128),
        (0, 0, 0),
        (0, 166, 153),
        (0, 154, 143),
        (0, 155, 141),
        (0, 155, 143),
        (0, 161, 148),
        (0, 158, 146),
    ]


def test_get_colors_from_large_image():
    result = get_colors_from("tests/files/cluster.png")
    # 500x325 image => 100x65 thumbnail
    assert len(result) == 100 * 65


def test_get_colors_from_animated_gif():
    result = get_colors_from("tests/files/Newtons_cradle.gif")
    # 480x360 image => 100x75 thumbnail
    # 36 frames, of which 18 are sampled
    assert len(result) == 100 * 75 * 18
    assert result[0:7500] != result[7500 : 7500 * 2]


# def test_choose_tint_color():
#     result = choose_tint_color(path='tests/files/cluster.png', background_color='white')
#     print(result)
