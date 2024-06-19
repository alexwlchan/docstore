import functools


class TagCloud:
    def __init__(self, tag_tally: dict[str, int]):
        self.tag_tally = tag_tally
        self.lowest_weight = min(tag_tally.values())
        self.highest_weight = max(tag_tally.values())
        self.range = (self.highest_weight - self.lowest_weight) or 1

        self.font_size_start = 10
        self.font_size_end = 24
        self.font_incr = (self.font_size_end - self.font_size_start) / self.range

        self.greyscale_start = 170
        self.greyscale_end = 70
        self.greyscale_incr = (self.greyscale_end - self.greyscale_start) / self.range

    @functools.lru_cache()
    def get_style(self, tag_count: int) -> str:
        weighting = tag_count - self.lowest_weight
        font_size = self.font_size_start + weighting * self.font_incr
        color = int(self.greyscale_start + weighting * self.greyscale_incr)
        return "font-size: %fpt; color: rgb(%d, %d, %d)" % (
            font_size,
            color,
            color,
            color,
        )
