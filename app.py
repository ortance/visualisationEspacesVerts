from __future__ import absolute_import
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import models
from models import *
import simplejson # possibilité d'afficher des données type Decimal
import geoalchemy2.functions as func
import json
import geojson
from sqlalchemy import *
from functions import format_geojson
# from tasks import test
from celery import Celery
import time


metadata = MetaData(db)

# on crée notre application
app = Flask(__name__)

celery = Celery(app.name, broker='amqp://hortense:perretho@localhost/virtual_host', backend='rpc://')
celery.conf.update(app.config)

app.config.from_object('config')
db.init_app(app)

@celery.task
def test(data_search):
    print ('long time task begins')
    run_script = passData.calcul(data_search)
    print ('long time task finished')
    return ('ok')

@app.route('/getFormData', methods=['POST'])
def get_javascript_data():
    params = request.json
    sunElevation = params['sunElevation']
    cloudCoverage = params['cloudCoverage']
    thresholdNDVI = params['thresholdNDVI']
    limitScene = params['limitScene']
    city = params['city']
    coords = params['coords']
    data_search = passData(sunElevation, cloudCoverage, thresholdNDVI, limitScene, city, coords)
    table = ndvi_auto('ndvi_'+ city)
    result = test.delay(data_search)
    return jsonify({'message': 'le traitement est en cours', 'bdd': 'ndvi_'+ city, 'id_task': result.id})
#
@app.route('/checkCeleryTask', methods=['POST'])
def state_celery_task():
    params = request.json
    table_name = params['table_name']
    id_task = params['id_task']
    res = test.AsyncResult(id_task)
    return jsonify({'state': res.ready(), 'table_name': table_name})

# ndvi issu du traitement par le script python
@app.route('/ndviAuto')
def get_ndviAuto():
    table_name = params['table_name']
    ndvi_table = ndvi_auto(table_name)
    query1 = select([ndvi_table.c.ogc_fid.label('ogc_fid'), func.ST_AsGeoJSON(func.ST_Transform(ndvi_table.c.wkb_geometry,4326)).label('wkb_geometry')]).where(ndvi_table.c.wkb_geometry!=None)
    dataQuery = db.session.execute(query1).fetchall()

    query2 = select([func.ST_AsText(func.ST_Centroid(func.ST_Extent(func.ST_Transform(func.ST_Transform(ndvi_table.c.wkb_geometry, 32631), 4326))))])
    dataQuery2 = db.session.execute(query2).fetchall()
    lat_center = float(dataQuery2[0][0][22:38])
    lng_center = float(dataQuery2[0][0][6:21])
    data_all = []
    data_all.append({'coords_center': {
                            'lat': lat_center,
                            'lng': lng_center
                            }
                        })
    for ndvi in dataQuery:
        ndvi = dict(ndvi)
        data_all.append({
                    'type': 'Feature',
                    'properties':{
                            'id':ndvi['ogc_fid'],
                        },
                    'geometry':json.loads(ndvi['wkb_geometry'])
                        })

    return jsonify(data_all)

if __name__ == '__main__':
    app.run()
