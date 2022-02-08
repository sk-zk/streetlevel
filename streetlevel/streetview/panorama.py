class StreetViewPanorama:
    def __init__(self, id, lat, lon):
        self.id = id
        self.lat = lat
        self.lon = lon

        self.month = None
        self.year = None

        self.country_code = None
        self.street_name = None

        self.neighbors = []
        self.historical = []

        self.tile_size = []
        self.image_sizes = []

    def __repr__(self):
        output = str(self)
        if self.year is not None and self.month is not None:
            output += f" [{self.year}-{self.month:02d}]"
        return output

    def __str__(self):
        return f"{self.id} ({self.lat:.6}, {self.lon:.6})"
