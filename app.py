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

# on crée un dictionnaire qui contient les différentes routes crées, associées à leur classe definies dans models.py
# dictClassData = {
# 'arr': Arrondissements,
# 'ndvi': Ndvi,
# 'esp': EspacesVerts,
# }

# on crée notre application
app = Flask(__name__)

celery = Celery(app.name, broker='amqp://hortense:perretho@localhost/virtual_host', backend='rpc://')
celery.conf.update(app.config)

app.config.from_object('config')
db.init_app(app)



# def make_celery(app):
#     celery = Celery('apiFlaskAlchemy', broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'],
#              include=['apiFlaskAlchemy.tasks'])
#     celery.conf.update(app.config)
#     TaskBase = celery.Task
#     class ContextTask(TaskBase):
#         abstract = True
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return TaskBase.__call__(self, *args, **kwargs)
#     celery.Task = ContextTask
#     return celery
#
# celery = make_celery(app)

# cette route, en mettant <obj>, on peut dans le navigateur y mettre la route qu'on veut, définie
# dans le dictionnaire au-dessus, et on récupère les propriétés
# @app.route('/<obj>/properties')
# def properties(obj):
#     # ici on regarde si l'objet rentré existe bien, sinon on lui donne la valeur none
#     dataObj = dictClassData.get(obj, None)
#     if not dataObj:
#         # dans ce cas, on retourne une erreur (chemin erroné)
#         return jsonify('error')
#     # ici, la route qu'on a rentré concerne un objet de type classe, on récupère les intitulés des colonnes
#     col = dictClassData[obj].__table__.c
#     value = []
#     for c in col:
#         value.append(c.key)
#     value.remove('geom')
#     print (value)
#     # on fait une liste compréhensive pour l'affichage
#     # return jsonify([c.key for c in col])
#     return jsonify([value])
#
# # on obtient le détail de la géometrie des polygones
# @app.route('/<obj>/geometry')
# def geometry(obj):
#     dataObj = dictClassData.get(obj, None)
#     if not dataObj:
#         return jsonify('error')
#     # on fait une requête pour ne sélectionner que les géométries, en faisant la transfromation en geojson
#     query = select([dictClassData[obj].gid.label('gid'), func.ST_AsGeoJSON(func.ST_Transform(dictClassData[obj].geom,4326)).label('geom')]).where(dictClassData[obj].geom!=None)
#     dataQuery = db.session.execute(query).fetchall()
#     geom_all = []
#     for data in dataQuery:
#         data = dict(data)
#         geom_all.append({
#                         'gid': data['gid'],
#                         'geometry': data['geom']
#                         })
#     return jsonify(geom_all)
#
# @app.route('/arr')
# def get_data():
#     data = Arrondissements.query.all()
#     data_all = []
#     return format_geojson(data)
# #
# @app.route('/esp')
# def get_esp():
#     # print(dict(request.data))
#     data = EspacesVerts.query.all()
#     data_all = []
#     return format_geojson(data)
#
# @app.route('/ndvi')
# def get_ndvi():
#     # print(dict(request.data))
#     # data = Ndvi.query.filter(Ndvi.geom!=None).all()
#     query = select([Ndvi.gid.label('gid'), func.ST_AsGeoJSON(func.ST_Transform(Ndvi.geom,4326)).label('geom')]).where(Ndvi.geom!=None)
#     dataQuery = db.session.execute(query).fetchall()
#     data_all = []
#
#     for ndvi in dataQuery:
#         ndvi = dict(ndvi)
#         data_all.append({
#                     'type': 'Feature',
#                     'properties':{
#                             'gid':ndvi['gid'],
#                         },
#                         'geometry':json.loads(ndvi['geom'])
#                         })
#     return jsonify(data_all)
#
@celery.task
def test(data_search):
    print ('long time task begins')
    run_script = passData.calcul(data_search)
    print ('long time task finished')
    return ('ok')
#
# @celery.task
# def test2(data_all, lat_center, lng_center, dataQuery):
#     print ('long time task begins')
#     data_all.append({'coords_center': {
#                             'lat': lat_center,
#                             'lng': lng_center
#                             }
#                             }
#                         )
#     for ndvi in dataQuery:
#         ndvi = dict(ndvi)
#         data_all.append({
#                     'type': 'Feature',
#                     'properties':{
#                             'id':ndvi['ogc_fid'],
#                         },
#                     'geometry':json.loads(ndvi['wkb_geometry'])
#                         })
#         print ('long time task finished')
#         return data_all

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
    # print(result.ready())
    # print(result.state())
    # print(type(result))
    # run_script = passData.calcul(data_search)
    # return jsonify(data_search.data_dict)
    return jsonify({'message': 'le traitement est en cours', 'bdd': 'ndvi_'+ city, 'id_task': result.id})
#
@app.route('/checkCeleryTask', methods=['POST'])
def state_celery_task():
    params = request.json
    table_name = params['table_name']
    id_task = params['id_task']
    # print(table_name, id_task)
    res = test.AsyncResult(id_task)
    # while res.ready() != True:
    #     time.sleep(5)
    #     print(res.ready())
    #     res = test.AsyncResult(id_task)
    return jsonify({'state': res.ready(), 'table_name': table_name})

# ndvi issu du traitement par le script python
@app.route('/ndviAuto')
def get_ndviAuto():
    a = len(db.engine.table_names())
    print(db.engine.table_names())
    ndvi_table = ndvi_auto(db.engine.table_names()[a-1])
    query1 = select([ndvi_table.c.ogc_fid.label('ogc_fid'), func.ST_AsGeoJSON(func.ST_Transform(ndvi_table.c.wkb_geometry,4326)).label('wkb_geometry')]).where(ndvi_table.c.wkb_geometry!=None)
    dataQuery = db.session.execute(query1).fetchall()

    query2 = select([func.ST_AsText(func.ST_Centroid(func.ST_Extent(func.ST_Transform(func.ST_Transform(ndvi_table.c.wkb_geometry, 32631), 4326))))])
    dataQuery2 = db.session.execute(query2).fetchall()
    lat_center = float(dataQuery2[0][0][22:38])
    lng_center = float(dataQuery2[0][0][6:21])
    # rows = (db.session.query(func.count()).select_from(ndvi_table)).scalar()
    data_all = []
    # test2.delay(data_all, lat_center, lng_center, dataQuery)
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
