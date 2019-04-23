# -*- encoding: utf-8

import datetime as dt


def relative_date_str(x, y):
    if x > y:
        diff = x - y
    else:
        diff = y - x

    if diff.total_seconds() < 60:
        return "just now"
    elif diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        assert minutes >= 1
        if minutes == 1:
            return "1 minute ago"
        else:
            return "%d minutes ago" % minutes
    elif diff.total_seconds() < 60 * 60 * 24:
        hours = int(diff.total_seconds() / (60 * 60))
        assert hours >= 1
        if hours == 1:
            return "1 hour ago"
        else:
            return "%d hours ago" % hours
    elif diff.total_seconds() < 60 * 60 * 24 * 7:
        days = int(diff.total_seconds() / (60 * 60 * 24))
        assert days >= 1
        if days == 1:
            return "1 day ago"
        else:
            return "%d days ago" % days
    else:
        return min([x, y]).strftime("%-d %b %Y")


def since_now_date_str(x):
    return relative_date_str(
        dt.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f"),
        dt.datetime.now()
    )
