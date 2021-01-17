import argparse
from dem2terrainrgb import Dem2TerrainRgb

def get_parser():
  prog = "dem2terrainrgb.py"
  parser = argparse.ArgumentParser(
      prog=prog,
      usage="%(prog)s --dem {dem file path} --dist {output directory path} --tmp {temporary directory path} --webp --remove_png --zoom {min-max zoom}",
      description="This module is to convert DEM to terrain RGB raster tiles."
  )

  parser.add_argument("--dem", dest="dem", required=True, help="Original DEM file. It must be already reprojected to EPSG:3857 before converting.")
  parser.add_argument("--dist", dest="dist", required=True, help="Output directory for tiles")
  parser.add_argument("--tmp", dest="tmp", required=False, default="./tmp", help="Temporary work directory")
  parser.add_argument('--webp', action='store_true', help="Use this option if you want to convert PNG to webp tiles")
  parser.add_argument('--remove_png', action='store_true', help="Use '--webp' option together. If this option is used, it will remove all of original PNG tiles.")
  parser.add_argument("--zoom", dest="zoom", required=False, default="5-15", help="Specify min-max zoom level for tiles. Default is 5-15.")

  return parser


if __name__ == "__main__":
  parser = get_parser()
  args = parser.parse_args()
  dem2terrain = Dem2TerrainRgb(args.dem, args.dist, args.tmp, args.zoom)
  filled_dem = dem2terrain.fill_nodata()
  rgbified_dem = dem2terrain.rgbify(filled_dem)
  dem2terrain.gdal2tiles(rgbified_dem)
  if args.webp:
    dem2terrain.png2webp(args.remove_png)

