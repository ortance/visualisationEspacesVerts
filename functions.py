from flask import Flask, request, jsonify, render_template
import requests
import json
import os
import urllib
import urllib.request
import rasterio
import numpy as np
import ogr
from osgeo import ogr, osr
from PIL import Image
from numpy import array
from rasterio import Affine
import subprocess
import gdal
import sys

def main_script(sunElevation, cloudCoverage, thresholdNDVI, limitScene, city, coords, dateBegin, dateEnd, dbName, user, host, port, password):
    EOS_API_KEY = os.environ['EOS_API_KEY']

    request_coords = []
    for i in range(0, len(coords)):
        request_coords.append([coords[i]['lng'], coords[i]['lat']])

    request_body = {
    "search": {
       "sunElevation": {"from":0,"to":sunElevation},
       "cloudCoverage": {"from":0,"to":cloudCoverage},
       "date": {"from":dateBegin,"to":dateEnd},
       "shape": {"type":"Polygon","coordinates":[
                    request_coords
       ]}
    },
    "page":1,
    "limit":limitScene,
    "fields":[
      "sceneID", "productName",
      "sunElevation", "cloudCoverage",
      "Date", "dataGeometry", "awsPath", "productPath", "sequence"
    ]
    }

    ri = requests.post('https://api.eos.com/v1/search/sentinel2',
    params = {'api_key':EOS_API_KEY},
    data = json.dumps(request_body))
    results = ri.json()['results']

    if ri.status_code != 200 or len(results) == 0:
        print("Il n'y a pas d'image correspondant à votre recherche")
    else:
        path = city
    if os.path.exists(path):
        print("Ce dossier existe déjà")
    else:
        owde = os.getcwd()
        os.mkdir(path)
        os.chdir(path)

        #################### téléchargement des bandes R et NIR et création d'un VRT ################################
        result = ri.json()['results']

        merge_command_B04 = ["gdalbuildvrt", "imageb4_vrt.vrt"]
        merge_command_B08 = ["gdalbuildvrt", "imageb8_vrt.vrt"]

        for imgData in result:
            owd = os.getcwd()
            path = '{}'.format(imgData['sceneID'])
            os.mkdir(path)
            os.chdir(path)
            download_sentinel2(imgData, 'B04')
            download_sentinel2(imgData, 'B08')
            os.chdir(owd)

            merge_command_B04.append(str(imgData['sceneID']) + '\B04.jp2')
            merge_command_B08.append(str(imgData['sceneID']) + '\B08.jp2')

        subprocess.call(merge_command_B04,shell=True)
        subprocess.call(merge_command_B08,shell=True)

        ##################### création d'un shapefile qui délimite la zone d'intérêt ###############
        coordinates = request_body["search"]["shape"]["coordinates"][int(0)]

        image = result[0]['sceneID'] + '\B04.jp2'
        with rasterio.open(image) as im:
            PROJ = im.read()
        profile = im.meta
        epsg = int(profile['crs']['init'][5:])

        new_coords = convert_coords(4326, epsg, coordinates)
        poly = create_polygon(new_coords)
        out_shp = r'polygonShape.shp'
        write_shapefile(poly, out_shp)
        projection(epsg)

        ###################### clip de l'image mergée en fonction du shapefile de la zone ###################
        clip_command_B04 = ["gdalwarp", "-cutline", out_shp, "-crop_to_cutline",
                            "imageb4_vrt.vrt", "clip_B04.tif"]
        clip_command_B08 = ["gdalwarp", "-cutline", out_shp, "-crop_to_cutline",
                            "imageb8_vrt.vrt", "clip_B08.tif"]
        subprocess.call(clip_command_B04)
        subprocess.call(clip_command_B08)

        ####################### calcul du ndvi #########################
        calculate_ndvi(r'ndvi_clip.tif')

        ####################### binarisation ###############
        thresholdNDVI = float(thresholdNDVI)
        binarize(r'ndvi_clip_binarized.tif', "ndvi_clip.tif", "binarized.tif", thresholdNDVI)

        ################# polygonisation et import dans PostgreSQL #################
        connect = "dbname=" + str(dbName) + " user=" + str(user) + " host=" + str(host) + " port=" + str(port) + " password=" + str(password)
        dbName, user, host, port, password
        gm = os.path.join('C:\\','OSGeo4W64','bin','gdal_polygonize.py')
        polygon_command = ["python", gm, "-mask",
                            "ndvi_clip_binarized.tif",
                            "ndvi_clip_binarized.tif", "-f", "PostgreSQL",
                            "PG:" + connect,
                            "ndvi_" + city]
        subprocess.call(polygon_command)

        os.chdir(owde)

#################### fonction pour télécharger la bande d'une image satellite, en fonction d'un jeu de résultat
def download_sentinel2(search_result, band, localpath='.'):
   search_result['awsPath']
   repository = 'http://sentinel-s2-l1c.s3.amazonaws.com'
   filename = '{}.jp2'.format(band)
   full_localname = '{}/{}.jp2'.format(localpath, band)
   url = '{}/{}/{}'.format(repository, search_result['awsPath'], filename)
   urllib.request.urlretrieve(url, full_localname)

######################## foncion pour créer un shapefile à partir des coordonnées de la recherche d'images
def convert_coords(srid_in, srid_out, coords):
    # mettre les coordonnées en 32631, UTM zone 31
    from pyproj import Proj, transform
    inProj = Proj(init='epsg:' + str(srid_in))
    outProj = Proj(init='epsg:' + str(srid_out))
    new_coords =[]
    count_coor = 0
    for c in coords:
        count_coor += 1
    for i in range(count_coor):
        new_coords.append(transform(inProj, outProj, coords[i][0], coords[i][1]))
    return new_coords

def create_polygon(coords):
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for coord in coords:
        ring.AddPoint(coord[0], coord[1])

    # Create polygon
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    return poly.ExportToWkt()

def write_shapefile(poly, out_shp):
    # Now convert it to a shapefile with OGR
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.CreateDataSource(out_shp)
    layer = ds.CreateLayer('', None, ogr.wkbPolygon)
    # Add one attribute
    defn = layer.GetLayerDefn()
    crs = layer.GetSpatialRef()

    # If there are multiple geometries, put the "for" loop here
    # Create a new feature (attribute and geometry)
    feat = ogr.Feature(defn)

    # Make a geometry, from Shapely object
    geom = ogr.CreateGeometryFromWkt(poly)
    feat.SetGeometry(geom)

    layer.CreateFeature(feat)
    feat = geom = None  # destroy these

    # Save and close everything
    ds = layer = feat = geom = None

# donner une projection au shapefile créé dans un fichier .prj
def projection(srid_out):
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromEPSG(srid_out)

    spatialRef.MorphToESRI()
    file = open('polygonShape.prj', 'w')
    file.write(spatialRef.ExportToWkt())
    file.close()

########################## fonction de calcul du ndvi
def calculate_ndvi(outfile):
    b4 = 'clip_B04.tif'
    b8 = 'clip_B08.tif'
    with rasterio.open(b4) as red:
        RED = red.read()
    with rasterio.open(b8) as nir:
        NIR = nir.read()
    np.seterr(divide='ignore', invalid='ignore')
    ndvi = (NIR.astype(float)-RED.astype(float))/(NIR+RED)

    profile = red.meta
    profile.update(driver='GTiff')
    profile.update(dtype=rasterio.float32)

    with rasterio.open(outfile, 'w', **profile) as dst:
        dst.write(ndvi.astype(rasterio.float32))

##################### fonction calcul vdvi
def calculate_vdvi(outfile):
    b2 = 'clip_B02.tif'
    b4 = 'clip_B04.tif'
    b3 = 'clip_B03.tif'
    with rasterio.open(b4) as red:
        RED = red.read()
    with rasterio.open(b3) as green:
        GREEN = green.read()
    with rasterio.open(b2) as blue:
        BLUE = blue.read()
    np.seterr(divide='ignore', invalid='ignore')
    vdvi = (2*(GREEN.astype(float))-RED.astype(float)-BLUE.astype(float))/(2*GREEN+RED+BLUE)

    profile = red.meta
    profile.update(driver='GTiff')
    profile.update(dtype=rasterio.float32)

    with rasterio.open(outfile, 'w', **profile) as dst:
        dst.write(vdvi.astype(rasterio.float32))

################### fonction pour binariser
def binarize(outfile, file_to_open, file_to_save, thresholdNDVI):
    # outfile = r'ndvi_clip_binarized.tif'
    img = Image.open(file_to_open)
    arr = array(img)
    w = arr.shape[0]
    h = arr.shape[1]

    for i in range(w):
        for j in range(h):
            if arr[i,j] > thresholdNDVI:
                arr[i,j]=1
            else:
                arr[i,j]=0

    img = Image.fromarray(arr)
    img.save(file_to_save)

    with rasterio.open(file_to_open) as ndvi_ras:
        RAS = ndvi_ras.read()

    profile = ndvi_ras.meta
    profile.update(driver='GTiff')
    profile.update(dtype=rasterio.float32)

    with rasterio.open(file_to_save) as binary:
        RAS = binary.read().astype(float)
    with rasterio.open(outfile, 'w', **profile) as dst:
        dst.write(RAS.astype(rasterio.float32))

# fonction qui permet formater en json les données des polygones, la classe concernée est définie dans data
def format_geojson(data):
    data_all = []

    for row in data:
        # on crée un dictionnaire contenant uniquement le type et les géométries pour l'instant
        curData = {'type': 'Feature',
                    'geometry': row.converted_geom # cette fonction est définie dans models.py
                    }
        # dans ce dictionnaire, on y rajoute un élément properties vide
        curData['properties'] = {}

        # pour chaque nom de colonne de la table du jeu de données, si la key est différente est différente de geom,
        # on récupère la valeur de la clé et on l'ajoute dans le dictionnaire
        for i in row.__table__.c:
            if i.key != 'geom':
                curData['properties'][i.key] = getattr(row,i.key)
        data_all.append(curData)

    return jsonify(data_all)
