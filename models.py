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
    def __init__(self, sunElevation, cloudCoverage, thresholdNDVI, limitScene, city, coords):
        self.sunElevation = sunElevation
        self.cloudCoverage = cloudCoverage
        self.thresholdNDVI = thresholdNDVI
        self.limitScene = limitScene
        self.city = city
        self.coords = coords
        self.coords.append(self.coords[0])
        self.data_dict = [{'sunElevation':self.sunElevation,
                            'cloudCoverage':self.cloudCoverage,
                            'thresholdNDVI':self.thresholdNDVI,
                            'limitScene':self.limitScene,
                            'city':self.city,
                            'coords':self.coords
                            }]

    def calcul(self):
        main_script(self.sunElevation, self.cloudCoverage, self.thresholdNDVI, self.limitScene, self.city, self.coords)
        return (print("traitement terminé"))


def ndvi_auto(city):
    return table(
        '{}'.format(city),
        db.Column('ogc_fid', db.Integer),
        db.Column('wkb_geometry', Geometry(geometry_type='POLYGON',
                                        srid=32631)))

# class NdviAuto(db.Model):
#     __tablename__ = engine.table_names()[a-1]
#     ogc_fid = db.Column(db.Integer, primary_key=True)
#     wkb_geometry = db.Column(Geometry(geometry_type='POLYGON', srid=32631))

# cette classe prend en entrée un objet, on fait hériter cette classe aux autres, la fonction de conversion
# de la géométrie se fera
class DbModelGeom(object):
    @hybrid_property
    def converted_geom(self):
        return geojson.loads(json.dumps(json.loads(db.session.scalar(func.ST_AsGeoJSON(func.ST_Transform(self.geom,4326))))))


# class EspacesVerts(db.Model, DbModelGeom):
#     __tablename__ = 'espaces_verts_urbains'
#
#     gid = db.Column(db.Integer, primary_key=True)
#     id = db.Column(db.Text)
#     code_12 = db.Column(db.Text)
#     area_ha = db.Column(db.Numeric)
#     geom = db.Column(Geometry(geometry_type='MULTIPOLYGON', srid=32631))
#
# class Arrondissements(db.Model, DbModelGeom):
#     __tablename__ = 'arrondissements'
#
#     gid = db.Column(db.Integer, primary_key=True)
#     osm_id = db.Column(db.Text)
#     name = db.Column(db.Text)
#     type = db.Column(db.Text)
#     geom = db.Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326))
#     prixmoy_m2 = db.Column(db.Numeric)
#
# class Ndvi(db.Model):
#     __tablename__ = 'ndvi_filtre'
#
#     gid = db.Column(db.Integer, primary_key=True)
#     geom = db.Column(Geometry(geometry_type='MULTIPOLYGON', srid=32631))
