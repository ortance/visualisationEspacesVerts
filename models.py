from sqlalchemy import Integer, Column, Text, Numeric, table, column
from geoalchemy2 import Geometry, Geography
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
import geojson, json
import geoalchemy2.functions as func
import requests
import json
from functions import *
import datetime

db = SQLAlchemy()

class passData():
    def __init__(self, sunElevation, cloudCoverage, thresholdNDVI, limitScene, city, coords, dateBegin, dateEnd, dbName, user, host, port, password):
        self.sunElevation = sunElevation
        self.cloudCoverage = cloudCoverage
        self.thresholdNDVI = thresholdNDVI
        self.limitScene = limitScene
        self.city = city
        self.coords = coords
        self.dateBegin = dateBegin
        self.dateEnd = dateEnd
        self.coords.append(self.coords[0])
        self.dbName = dbName
        self.user = user
        self.host = host
        self.port = port
        self.password = password

        self.data_dict = [{'sunElevation':self.sunElevation,
                            'cloudCoverage':self.cloudCoverage,
                            'thresholdNDVI':self.thresholdNDVI,
                            'limitScene':self.limitScene,
                            'city':self.city,
                            'dateBegin':self.dateBegin,
                            'dateEnd':self.dateEnd,
                            'coords':self.coords
                            }]

    def calcul(self):
        main_script(self.sunElevation, self.cloudCoverage, self.thresholdNDVI, self.limitScene, self.city, self.coords, self.dateBegin, self.dateEnd, self.dbName, self.user, self.host, self.port, self.password)
        return (print("traitement terminé"))


def ndvi_auto(table_name, epsg):
    return table(
        '{}'.format(table_name),
        db.Column('ogc_fid', db.Integer),
        db.Column('wkb_geometry', Geometry(geometry_type='POLYGON',
                                        srid=epsg)))

# cette classe prend en entrée un objet, on fait hériter cette classe aux autres, la fonction de conversion
# de la géométrie se fera
class DbModelGeom(object):
    @hybrid_property
    def converted_geom(self):
        return geojson.loads(json.dumps(json.loads(db.session.scalar(func.ST_AsGeoJSON(func.ST_Transform(self.geom,4326))))))
