# dem2terrainrgb
![GitHub](https://img.shields.io/github/license/watergis/dem2terrainrgb)

This module is to convert DEM to terrain RGB raster tiles.

## Installation

```
cd dem2terrainrgb
pipenv install
```

## Usage

```
$ python main.py -h
usage: dem2terrainrgb.py --dem {dem file path} --dist {output directory path} --tmp {temporary directory path} --webp --remove_png --zoom {min-max zoom}

This module is to convert DEM to terrain RGB raster tiles.

optional arguments:
  -h, --help    show this help message and exit
  --dem DEM     Original DEM file. It must be already reprojected to EPSG:3857 before converting.
  --dist DIST   Output directory for tiles
  --tmp TMP     Temporary work directory
  --webp        Use this option if you want to convert PNG to webp tiles
  --remove_png  Use '--webp' option together. If this option is used, it will remove all of original PNG tiles.
  --zoom ZOOM   Specify min-max zoom level for tiles. Default is 5-15.
```

The below is an example command. Before executing this module, you must reproject your DEM to EPSG:3857 coordinates by using GDAL or QGIS.
```
pipenv shell
python main.py --dem ./data/rwanda_dem_EPSG3857_10m.tif --dist ./tiles --webp --zoom 5-15
```

Finally, you can delete all of xml files under tiles folder.
```
find ./tiles -name "*.xml" -exec bash -c 'rm "$1"' - '{}' \;
```

## Validation

If you want to validate processed tiff image, you can command like below.

```
$ rio info --indent 2 ./data/rwanda_dem_EPSG3857_10m_without_nodata.tif
```

<details>

```json
{
  "blockxsize": 256,
  "blockysize": 256,
  "bounds": [
    3223733.0877,
    -316437.17616185057,
    3439718.7685284764,
    -115768.6321
  ],
  "colorinterp": [
    "gray"
  ],
  "compress": "deflate",
  "count": 1,
  "crs": "EPSG:3857",
  "descriptions": [
    null
  ],
  "driver": "GTiff",
  "dtype": "uint16",
  "height": 19992,
  "indexes": [
    1
  ],
  "interleave": "band",
  "lnglat": [
    29.92940323722318,
    -1.9409140983431143
  ],
  "mask_flags": [
    [
      "all_valid"
    ]
  ],
  "nodata": null,
  "res": [
    10.037442179964515,
    10.037442179964515
  ],
  "shape": [
    19992,
    21518
  ],
  "tiled": true,
  "transform": [
    10.037442179964515,
    0.0,
    3223733.0877,
    0.0,
    -10.037442179964515,
    -115768.6321,
    0.0,
    0.0,
    1.0
  ],
  "units": [
    null
  ],
  "width": 21518
}
```
</details>

For verifying the elevation data, you may do the below command.

```
$ gdallocationinfo -wgs84 ./data/rwanda_dem_EPSG3857_10m_RGB.tif 29.7363 -2.2313
Report:
  Location: (8617P,13218L)
  Band 1:
    Value: 1
  Band 2:
    Value: 199
  Band 3:
    Value: 250
(rwanda_terrain)
```

Formula is like this:

```
height = -10000 + ((R * 256 * 256 + G * 256 + B) * 0.1)
```

## Convert to MBTiles

You can use mb-util module to convert tilesets into a mbtiles container.

```
$ mb-util --image_format=png --scheme=xyz ./tiles/ ./tilesets/rwanda_dem_EPSG3857_10m.mbtiles
```

If you want to create mbtiles from webp tiles, the command should be like below.
```
$ mb-util --image_format=webp --scheme=xyz ./tiles/ ./tilesets/rwanda_dem_EPSG3857_10m_webp.mbtiles
```

Before running `mb-util`, don't forget to put `metadata.json` under `tiles` folder. The below is an example of content for `metadata.json`.

```json
{
  "name": "Rwanda 10m Terrain RGB Tileset",
  "description": "Rwanda 10m Terrain RGB Tileset, CC-BY-4.0: Water and Sanitation Corporation (WASAC), Rwanda",
  "version": "1"
}
```

## Tile hosting

You can upload tilesets to Github pages for hosting. If you would like to host tiles on your own server, you may be able to use [mbtilesserver](https://github.com/consbio/mbtileserver).

After installing `mbtileserver`,

```
~/go/bin/mbtileserver --verbose
```

it will automatically find mbtiles under `tilesets` folder, then access to [http://localhost:8000/services](http://localhost:8000/services). You will see the following response.

```json
[
    {
        "imageType": "png",
        "url": "http://localhost:8000/services/rwanda_dem_EPSG3857_10m",
        "name": "Rwanda 10m Terrain RGB Tileset"
    }
]
```

After that, continue to access [http://localhost:8000/services/rwanda_dem_EPSG3857_10m](http://localhost:8000/services/rwanda_dem_EPSG3857_10m) and see more detailed information.

```json
{
    "description": "Rwanda 10m Terrain RGB Tileset, CC-BY-4.0: Water and Sanitation Corporation (WASAC), Rwanda",
    "format": "png",
    "map": "http://localhost:8000/services/rwanda_dem_EPSG3857_10m/map",
    "maxzoom": 15,
    "minzoom": 5,
    "name": "Rwanda 10m Terrain RGB Tileset",
    "scheme": "xyz",
    "tilejson": "2.1.0",
    "tiles": [
        "http://localhost:8000/services/rwanda_dem_EPSG3857_10m/tiles/{z}/{x}/{y}.png"
    ],
    "version": "1"
}
```

Tileset URL will be as below.
```
http://localhost:8000/services/rwanda_dem_EPSG3857_10m/tiles/{z}/{x}/{y}.png
```