#!/usr/bin/env python3
from osgeo import gdal, ogr
import numpy as np
import os

VEGETATIVE_INDEX = 0.15

# Return the raster's folder string
def getRasterFolder():
    flag = True
    while flag:
        print("Type the full path of the raster folder:")
        raster_folder = str(input())
        
        if os.path.isdir(raster_folder):
            flag = False
        else:
            print("The path you entered doesn't exist or isn't a directory!")
    
    return raster_folder

# Check if the file passed as an argument is of type "shapefile"
def isValidShape(vector_file):
    try:
        driver = ogr.GetDriverByName('ESRI Shapefile')
        dataSource = driver.Open(vector_file, 0)
        if dataSource is None:
            return False
        layer = dataSource.GetLayer()
        return True
    except:
        return False

# Return the Vector's file path string
def getVectorPath():
    flag = True
    while flag:
        print("Type the full path of the vector file (shapefile):")
        vector_file = str(input())
        
        if isValidShape(vector_file):
            flag = False
        else:
            print("The path you entered isn't a shapefile!")
    
    return vector_file

# Open the original raster file, create a new raster based on the vegetative 
# index and polarize it. Where values above a given vegetation index are assigned 
# 1 and values below are assigned 0.
def polarizeRaster(raster_file):
    # Opens the tiff file
    ds = gdal.Open(raster_file.path)
    # Get some Geo information
    gt = ds.GetGeoTransform()
    # Get the file projection
    proj = ds.GetProjection()
    # Stores the different bands of the file (RED and GREEN)
    red_band = ds.GetRasterBand(1).ReadAsArray().astype(np.float32)
    green_band = ds.GetRasterBand(2).ReadAsArray().astype(np.float32)

    new_band = (green_band - red_band) / (green_band + red_band)

    # Creating the new band/raster based on the vegetative index
    binmask = np.where((new_band >= VEGETATIVE_INDEX), 1, 0)

    driver = gdal.GetDriverByName("GTiff")
    driver.Register()
    polarized_name = "raster_polarized/" + raster_file.name.split(".tif")[0] + "-polarized.tif"
    outds = driver.Create(polarized_name, xsize = binmask.shape[1],
                        ysize = binmask.shape[0], bands = 1,
                        eType = gdal.GDT_Float32)

    outds.SetGeoTransform(gt)
    outds.SetProjection(proj)
    outband = outds.GetRasterBand(1)
    outband.WriteArray(binmask)
    outband.SetNoDataValue(np.nan)
    outband.FlushCache()

    outband = None 
    outds = None

    return polarized_name

# Crop the raster based on a vector "shapefile"
def clipRaster(polarized_name, vector_path):
    raster = gdal.Open(polarized_name)

    options = gdal.WarpOptions(cutlineDSName=vector_path, cropToCutline=True, dstNodata=0)
    gdal.Warp(polarized_name, raster, options=options)

    raster = None

# Transforms a raster into a vector with a polygonization
def polygonizeRaster(polarized_name):
    raster = gdal.Open(polarized_name)
    polygonized_name = polarized_name.split("polarized.tif")[0] + "polygonized.shp"

    band = raster.GetRasterBand(1)
    band.SetNoDataValue(0)

    mask_band = band.GetMaskBand()

    driver = ogr.GetDriverByName('ESRI Shapefile')

    out_ds = driver.CreateDataSource(polygonized_name)
    out_layer = out_ds.CreateLayer('polygons', geom_type=ogr.wkbPolygon)

    field_def = ogr.FieldDefn('DN', ogr.OFTInteger)
    out_layer.CreateField(field_def)

    gdal.Polygonize(band, mask_band, out_layer, 0)

    out_ds = None
    raster = None

def main():
    raster_folder = getRasterFolder()
    vector_path = getVectorPath()
    
    with os.scandir(raster_folder) as raster_files:
        for raster_file in raster_files:
            polarized_name = polarizeRaster(raster_file)
            clipRaster(polarized_name, vector_path)
            polygonizeRaster(polarized_name)
            os.remove(polarized_name)

if __name__ == "__main__":
    main()