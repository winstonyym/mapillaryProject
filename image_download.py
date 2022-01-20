import mercantile, mapbox_vector_tile, requests, json, os
from vt2geojson.tools import vt_bytes_to_geojson

# define an empty geojson as output
output= { "type": "FeatureCollection", "features": [] }

# vector tile endpoints -- change this in the API request to reference the correct endpoint
tile_coverage = 'mly1_public'

# tile layer depends which vector tile endpoints:
# 1. if map features or traffic signs, it will be "point" always
# 2. if looking for coverage, it will be "image" for points, "sequence" for lines, or "overview" for far zoom
tile_layer = 'image'

# Mapillary access token -- user should provide their own
access_token = 'MLY|4826481817389593|29f5db2b7826a5845bc2ee8d2fc8e1b1'

# a bounding box in [east_lng,_south_lat,west_lng,north_lat] format
west, south, east, north = [103.6920359, 1.1304753 , 104.0120359, 1.4504753]

# get the list of tiles with x and y coordinates which intersect our bounding box
# MUST be at zoom level 14 where the data is available, other zooms currently not supported
tiles = list(mercantile.tiles(west, south, east, north, 14))

for tile in tiles[1]:
    tile_url = 'https://tiles.mapillary.com/maps/vtp/{}/2/{}/{}/{}?access_token={}'.format(tile_coverage,tile.z,tile.x,tile.y,access_token)
    response = requests.get(tile_url)
    data = vt_bytes_to_geojson(response.content, tile.x, tile.y, tile.z)

    # push to output geojson object if yes
    for feature in data['features']:
      if feature['geometry']['type'] == 'Point':
        # get lng,lat of each feature
          lng = feature['geometry']['coordinates'][0]
          lat = feature['geometry']['coordinates'][1]

        # ensure feature falls inside bounding box since tiles can extend beyond
          if lng > west and lng < east and lat > south and lat < north:
              sequence_id = feature['properties']["sequence_id"]
              if not os.path.exists(sequence_id):
                os.makedirs(sequence_id)

          # request the URL of each image
          image_id = feature['properties']['id']
          url = 'https://graph.mapillary.com/{}?fields=thumb_2048_url&access_token={}'.format(image_id, access_token)
          r = requests.get(url, headers=header)
          data = r.json()
          image_url = data['thumb_2048_url']

              # save each image with ID as filename to directory by sequence ID
          with open('{}/{}.jpg'.format(sequence_id, image_id), 'wb') as handler:
              image_data = requests.get(image_url, stream=True).content
              handler.write(image_data)

      else:
          pass
