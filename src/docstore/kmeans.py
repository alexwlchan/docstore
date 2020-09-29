import math
import random


def euclidean_distance(x, y):
    """
    Returns the Euclidean distance between two points.
    """
    assert len(x) == len(
        y
    ), f"Points must have the same number of dimensions: x={x!r}, y={y!r}"
    return math.sqrt(sum((x_i - y_i) ** 2 for (x_i, y_i) in zip(x, y)))


def calculate_centre(points):
    """
    Given a collection of points, calculate the centre.

    Here the "centre" is found by computing the mean of each dimension independently.
    """
    dimensions = {len(p) for p in points}
    assert (
        len(dimensions) == 1
    ), f"Points must have the same number of dimensions: {dimensions}"

    dimensions = dimensions.pop()

    return tuple(
        (sum(p[dim] for p in points) / len(points)) for dim in range(dimensions)
    )


def kmeans(points, *, k, threshold=0):
    """
    Find the result of a k-means clustering over ``points``.

    :param k: The number of clusters to create.
    :param threshold: If the difference between iterations is less than `threshold`,
        stop the iteration.
    """
    assert threshold >= 0

    # Choose k points at random as the initial means.
    means = random.sample(points, k)

    while True:
        # For each point, find the closest mean, and put that point in
        # a cluster with that mean.
        clusters = {m: set() for m in means}

        for p in points:
            closest_mean = min(means, key=lambda m: euclidean_distance(m, p))
            clusters[closest_mean].add(p)

        # Calculate the centre of each cluster, and use that as the
        # new mean.
        new_means_distance = 0
        means = []

        for mean, points_in_cluster in clusters.items():
            new_mean = calculate_centre(points_in_cluster)
            means.append(new_mean)

            new_means_distance += euclidean_distance(mean, new_mean)

        # If the means have stopped changing, then the clusters have
        # converged, and we can terminate.
        if new_means_distance <= threshold:
            return means
