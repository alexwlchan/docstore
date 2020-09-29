from docstore.kmeans import kmeans


def test_kmeans_on_two_points():
    assert kmeans(points=[(1, 1), (0, 0)], k=1) == [(0.5, 0.5)]


def test_kmeans_on_four_points():
    points = [(0, 0), (1, 1), (9, 9), (10, 10)]
    result = kmeans(points, k=2)
    assert result == [(0.5, 0.5), (9.5, 9.5)] or result == [(9.5, 9.5), (0.5, 0.5)]
