class StreetsidePanorama:
    def __init__(self, id, lat, lon):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.date = None
        self.next = None
        self.previous = None
        self.altitude = None

    def __repr__(self):
        output = str(self)
        if self.date is not None:
            output += f" [{self.date}]"
        return output

    def __str__(self):
        return f"{self.id} ({self.lat:.6}, {self.lon:.6})"
