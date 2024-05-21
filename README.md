# polygonization-script
This script was created to automate part of a drone image processing protocol. Polarizing the raster file, cropping it based on a vector file and converting it using polygonization.

At the moment, the script only supports polarization by vegetative index, but there are plans to support polarization based on other characteristics soon.

## Requirements
- Python's libraries GDAL and numpy. You can install these libraries with pip (Python's default package manager).
```
pip install gdal
```
```
pip install numpy
```
- Folder with raster files.
- Folder for output files called "raster-polarized"
- Vector file (used to crop the original raster)

## How to use
You can run the script with the following command:
### Linux
```
./final-script.py
```
### Windows
```
python final-script.py
```

After you start the script, it will ask you to type the path to raster's folder and the vector file. Example in Linux:
```
./final-script.py
Type the full path of the raster folder:
raster_og/
Type the full path of the vector file (shapefile):
vector-files/vector-python.shp
```
Then, the script will fully execute and generate the converted files.
