import rasterio
import rasterio.plot
from rasterio.crs import CRS
from rasterio.warp import reproject, Resampling

data = "/home/gaia/Documents/SdF/stromboli_xyz_geo.tif" ##UTM
#data = "/home/gaia/Documents/SdF/test/test.tiff" ## NOT UTM
dataset = rasterio.open(data)
rasterio.plot.show(dataset)

#tiff.bounds: indicates the spatial bounding box
#tiff.count: number of bands
#tiff.width: number of columns of the raster dataset
#tiff.height: number of rows of the raster dataset
#tiff.crs: coordinate reference system

print(dataset.bounds)
print(dataset.count)
print(dataset.height)
print(dataset.width)
print(dataset.height*dataset.width)
print(dataset.crs)
print(dataset.name)
print(dataset.mode) ## si tu lis le fichier ou si tu l'écris ou si je sais pas 
print(data.count)
#{i: dtype for i, dtype in zip(dataset.indexes, dataset.dtypes)}
#print(dataset.indexes)
#print(dataset.dtypes)
#print(dataset.transform)

band1 = dataset.read(1)
print(band1)
print(len(band1))
print(band1[0])
print(band1[dataset.height // 2, dataset.width // 2]) ## renvoie le numéro du pixel au centre

row=1
col=1
print(band1[row, col]) ## renvoie la valeur du pixel

print(dataset.tags())

print("Coordonnées de la première valeur du raster (en UTM):")
print(dataset.transform * (0, 0))  # Affiche les coordonnées en UTM du coin supérieur gauche

