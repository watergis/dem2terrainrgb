import argparse
from dem2terrainrgb import Dem2TerrainRgb

def get_parser():
  prog = "dem2terrainrgb.py"
  parser = argparse.ArgumentParser(
      prog=prog,
      usage="%(prog)s --dem {dem file path} --dist {output directory path}",
      description="This module is to convert DEM to terrain RGB raster tiles."
  )

  parser.add_argument("--dem", dest="dem", required=True, help="Original DEM file. It must be already reprojected to EPSG:3857 before converting.")
  parser.add_argument("--dist", dest="dist", required=True, help="Output directory for tiles")
  parser.add_argument("--tmp", dest="tmp", required=False, default="./tmp", help="Temporary work directory")
  parser.add_argument('--webp', action='store_true', help="Use this option if you want to convert PNG to webp tiles")

  return parser


if __name__ == "__main__":
  parser = get_parser()
  args = parser.parse_args()
  dem2terrain = Dem2TerrainRgb(args.dem, args.dist, args.tmp)
  filled_dem = dem2terrain.fill_nodata()
  rgbified_dem = dem2terrain.rgbify(filled_dem)
  dem2terrain.gdal2tiles(rgbified_dem)
  if args.webp:
    dem2terrain.png2webp()

