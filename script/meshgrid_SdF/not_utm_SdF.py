import rasterio
import rasterio.plot
from rasterio.crs import CRS
from rasterio.warp import reproject, Resampling
from rasterio.plot import show
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

data = "/home/gaia/Documents/SdF/not_utm/not_utm.tiff"
dataset = rasterio.open(data)
rasterio.plot.show(dataset)

visu_data=dataset.read()
print(visu_data)

print(visu_data.shape)
print(visu_data.dtype)
print(visu_data.min)

#tiff.bounds: indicates the spatial bounding box
#tiff.count: number of bands
#tiff.width: number of columns of the raster dataset
#tiff.height: number of rows of the raster dataset
#tiff.crs: coordinate reference system

#print(dataset.bounds)
#print(dataset.count)
#print(dataset.height)
#print(dataset.width)
#print(dataset.height*dataset.width)
#print(dataset.crs)
#print(dataset.name)
#print(dataset.mode) ## si tu lis le fichier ou si tu l'écris ou si je sais pas 
#print(data.count)
#{i: dtype for i, dtype in zip(dataset.indexes, dataset.dtypes)}
#print(dataset.indexes)
#print(dataset.dtypes)
#print(dataset.transform)

#band1 = dataset.read(1)
#print(band1)
#print(len(band1))
#print(band1[0])
#print(band1[dataset.height // 2, dataset.width // 2]) ## renvoie le numéro du pixel au centre

#row=0
#col=0
#print(band1[row, col]) ## renvoie la valeur du pixel

#print(dataset.tags())

data = "/home/gaia/Documents/SdF/test/test.tiff"

with rasterio.open(data) as src:
    band1 = src.read(1)

    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111, projection='3d')

    x = np.arange(band1.shape[1])
    y = np.arange(band1.shape[0])
    x, y = np.meshgrid(x, y)

    ax.plot_surface(x, y, band1, cmap='viridis', rstride=1, cstride=1, edgecolor='none')

    fig.colorbar(ax.plot_surface(x, y, band1, cmap='viridis', rstride=1, cstride=1, edgecolor='none'))

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Elevation')

plt.tight_layout()
plt.show()


