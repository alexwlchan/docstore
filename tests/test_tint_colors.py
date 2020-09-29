from docstore.tint_colors import get_colors_from


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
    result = get_colors_from('tests/files/cluster.png')
    # 500x325 image => 100x65 thumbnail
    assert len(result) == 6500
