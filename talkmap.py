# Leaflet cluster map of talk locations
#
# Run this from the repository root. For each talk in _talks/, a pin is placed
# using the talk's latitude/longitude fields if they are given; otherwise the
# location field is looked up in OpenStreetMap (geopy/Nominatim). Talks with no
# location, or a location of "Virtual", "Online" or "Remote", are left off the
# map. The getorg library then writes the HTML and Javascript for the map.
import frontmatter
import glob
import getorg
from geopy import Nominatim
from geopy.point import Point

TIMEOUT = 5  # seconds to wait for each OpenStreetMap lookup
geocoder = Nominatim(user_agent="academicpages.github.io")
location_dict = {}

for file in sorted(glob.glob("_talks/*.md")):
    data = frontmatter.load(file).to_dict()

    title = str(data.get('title') or '').strip()
    venue = str(data.get('venue') or '').strip()
    location = str(data.get('location') or '').strip()
    description = f"{title}<br />{venue}; {location}"

    # 1. Use coordinates from the front matter when they are given
    lat, lon = data.get('latitude'), data.get('longitude')
    if lat is not None and lon is not None:
        try:
            location_dict[description] = Point(float(lat), float(lon))
            print(f"{file}: using coordinates {lat}, {lon}")
        except ValueError as ex:
            print(f"{file}: could not use latitude/longitude ({lat}, {lon}): {ex}")
        continue

    # 2. Leave talks with no physical location off the map
    if location == '' or location.lower() in ('virtual', 'online', 'remote'):
        print(f"{file}: no physical location, not mapped")
        continue

    # 3. Otherwise look the location up in OpenStreetMap
    try:
        result = geocoder.geocode(location, timeout=TIMEOUT)
        location_dict[description] = result
        print(f"{file}: looked up '{location}' -> {result}")
    except Exception as ex:
        print(f"{file}: lookup failed for '{location}': {ex}")

getorg.orgmap.output_html_cluster_map(location_dict, folder_name="talkmap", hashed_usernames=False)
