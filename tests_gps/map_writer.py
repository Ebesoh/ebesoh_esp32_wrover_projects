"""
map_writer.py

Creates and updates a KML file for Google Maps / Google Earth:
- Red = Raw GPS
- Blue = Filtered GPS
"""

class KMLWriter:
    def __init__(self, filename="gps_tracks.kml"):
        self.filename = filename
        self.raw_points = []
        self.filt_points = []
        self._write_kml_header()

    def add_point(self, raw_lat, raw_lon, filt_lat, filt_lon):
        self.raw_points.append((raw_lat, raw_lon))
        self.filt_points.append((filt_lat, filt_lon))
        self._write_kml()

    def _write_kml_header(self):
        with open(self.filename, "w") as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<name>GPS Raw vs Filtered</name>
</Document>
</kml>
""")

    def _write_kml(self):
        with open(self.filename, "w") as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<name>GPS Raw vs Filtered</name>

<Style id="rawStyle">
  <LineStyle>
    <color>ff0000ff</color>
    <width>3</width>
  </LineStyle>
</Style>

<Style id="filtStyle">
  <LineStyle>
    <color>ffff0000</color>
    <width>3</width>
  </LineStyle>
</Style>

<Placemark>
  <name>Raw GPS Track</name>
  <styleUrl>#rawStyle</styleUrl>
  <LineString>
    <tessellate>1</tessellate>
    <coordinates>
""")

            for lat, lon in self.raw_points:
                f.write(f"{lon},{lat},0\n")

            f.write("""
    </coordinates>
  </LineString>
</Placemark>

<Placemark>
  <name>Filtered GPS Track</name>
  <styleUrl>#filtStyle</styleUrl>
  <LineString>
    <tessellate>1</tessellate>
    <coordinates>
""")

            for lat, lon in self.filt_points:
                f.write(f"{lon},{lat},0\n")

            f.write("""
    </coordinates>
  </LineString>
</Placemark>

</Document>
</kml>
""")
