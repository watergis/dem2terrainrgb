import subprocess
import os
import shutil
import glob
from PIL import Image
from tqdm import tqdm


class Dem2TerrainRgb(object):
  """
  Class for converting DEM file to terrain RGB raster tilesets.
  This source code was inspired from the below repository.

  https://github.com/syncpoint/terrain-rgb
  """

  def __init__(self, dem, dist, tmp) -> None:
    """Constructor

    Args:
        dem (str): DEM file path. The DEM file must be reprojected to EPSG:3857 before converting.
        dist ([type]): Output directory for terrain RGB tiles
        tmp ([type]): Temporary directory for work
    """
    self.dem = dem
    self.dist = dist
    self.tmp = tmp

  def fill_nodata(self):
    """
    Fill NO DATA value. Before we rgbify, all of NO DATA values need to be filled.

    After this process, you may validate the converted tiff by following command.

    $ rio info --indent 2 ./data/rwanda_dem_EPSG3857_10m_without_nodata.tif

    Returns:
        str: Filled DEM file path
    """
    if not os.path.exists(self.tmp):
      os.makedirs(self.tmp)
    filename = os.path.splitext(os.path.basename(self.dem))[0]
    filled_file = f"{self.tmp}/{filename}_without_nodata.tif"

    if os.path.exists(filled_file):
      os.remove(filled_file)

    cmd = f"gdalwarp \
          -t_srs EPSG:3857 \
          -dstnodata None \
          -co TILED=YES \
          -co COMPRESS=DEFLATE \
          -co BIGTIFF=IF_NEEDED \
          {self.dem} \
          {filled_file}"
    subprocess.check_output(cmd, shell=True)
    print(f"filled NODATA value successfully: {filled_file}")
    return filled_file

  def rgbify(self, filled_dem):
    """
    transform the greyscale data into the RGB data. The formula used to calculate the elevation is

    height = -10000 + ((R * 256 * 256 + G * 256 + B) * 0.1)
    So the base value is -10000 and the interval (precision of the output) is 0.1.

    After rgbfying, you can validate by following command.
    
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

    Args:
        filled_dem ([type]): [description]

    Returns:
        [type]: [description]
    """
    filename = os.path.splitext(os.path.basename(self.dem))[0]
    rgbified_dem = f"{self.tmp}/{filename}_RGB.tif"

    if os.path.exists(rgbified_dem):
      os.remove(rgbified_dem)

    cmd = f"rio rgbify \
          -b -10000 \
          -i 0.1 \
          {filled_dem} \
          {rgbified_dem}"

    subprocess.check_output(cmd, shell=True)
    print(f"rgbified successfully: {rgbified_dem}")
    return rgbified_dem

  def gdal2tiles(self, rgbified_dem):
    """Generate tiles as PNG format.
    see about gdal2tiles:
    https://gdal.org/programs/gdal2tiles.html
    Args:
        rgbified_dem (str): Rgbified DEM file path

    Returns:
        str: Output directory path
    """
    if os.path.exists(self.dist):
      shutil.rmtree(self.dist)

    cmd = f"gdal2tiles.py \
          --zoom=5-15 \
          --resampling=near \
          --tilesize=512 \
          --processes=8 \
          --xyz {rgbified_dem} \
          {self.dist}"

    subprocess.check_output(cmd, shell=True)
    print(f"created tileset successfully: {self.dist}")
    return self.dist

  def png2webp(self):
    files = glob.glob(self.dist + '/**/*.png', recursive=True)
    for file in tqdm(files):
      img = Image.open(file)
      img.save(file.replace('.png','.webp'), "WEBP", lossless=True)
      os.remove(file)