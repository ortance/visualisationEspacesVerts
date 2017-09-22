# à placer au même niveau que code_visualisationEV dans l'arborescence des fichiers

import os

from setuptools import setup, find_packages

requires = [
    'affine==2.0.0.post1',
    'amqp==1.4.9',
    'anyjson==0.3.3',
    'arcgis==1.2.0',
    'Babel==2.4.0',
    'billiard==3.3.0.23',
    'bleach==1.5.0',
    'boto3==1.4.4',
    'botocore==1.5.55',
    'celery==3.1.24',
    'certifi==2016.2.28',
    'cffi==1.9.1',
    'click==6.7',
    'click-plugins==1.0.3',
    'cligj==0.4.0',
    'colorama==0.3.9',
    'conda==4.3.25',
    'coverage==4.3.4',
    'cryptography==1.7.1',
    'cycler==0.10.0',
    'decorator==4.0.11',
    'defusedxml==0.5.0',
    'descartes==1.1.0',
    'docutils==0.13.1',
    'entrypoints==0.2.3',
    'Fiona==1.7.8',
    'Flask==0.12.2',
    'Flask-Login==0.4.0',
    'flask-openid==1.2.5',
    'Flask-SQLAlchemy==2.2',
    'Flask-WTF==0.14.2',
    'flower==0.9.2',
    'GDAL==2.2.0',
    'geoalchemy2==0.4.0',
    'geojson==1.3.5',
    'geopandas==0.2.1',
    'glob2==0.5',
    'html5lib==0.999',
    'idna==2.2',
    'image-slicer==0.1.1',
    'ipykernel==4.6.1',
    'ipython==6.1.0',
    'ipython-genutils==0.2.0',
    'ipywidgets==6.0.0',
    'itsdangerous==0.24',
    'jedi==0.10.2',
    'Jinja2==2.9.6',
    'jmespath==0.9.2',
    'jsonschema==2.6.0',
    'jupyter-client==5.1.0',
    'jupyter-core==4.3.0',
    'kerberos-sspi==0.2',
    'kombu==3.0.37',
    'MarkupSafe==0.23',
    'matplotlib==2.0.2',
    'menuinst==1.4.4',
    'mistune==0.7.4',
    'munch==2.1.1',
    'nbconvert==5.2.1',
    'nbformat==4.3.0',
    'notebook==5.0.0',
    'numpy==1.12.1',
    'olefile==0.44',
    'pandas==0.20.1',
    'pandocfilters==1.4.1',
    'path.py==10.3.1',
    'pickleshare==0.7.4',
    'Pillow==4.1.1',
    'planet==1.0.0',
    'prompt-toolkit==1.0.14',
    'psycopg2==2.7.1',
    'pyasn1==0.2.3',
    'pycosat==0.6.2',
    'pycparser==2.17',
    'Pygments==2.2.0',
    'pyOpenSSL==16.2.0',
    'pyparsing==2.2.0',
    'pyproj==1.9.5.1',
    'PySAL==1.13.0',
    'pyshp==1.2.11',
    'python-dateutil==2.6.0',
    'python3-openid==3.1.0',
    'pytz==2017.2',
    'pywin32==221',
    'pyzmq==16.0.2',
    'rasterio==1.0a9',
    'requests==2.14.2',
    'requests-futures==0.9.7',
    'Rtree==0.8.3',
    'ruamel-yaml==0.11.14',
    's3transfer==0.1.10',
    'scipy==0.19.0',
    'Shapely==1.5.17.post1',
    'simplegeneric==0.8.1',
    'simplejson==3.10.0',
    'six==1.10.0',
    'snuggs==1.4.1',
    'SQLAlchemy==1.1.9',
    'sqlalchemy-migrate==0.11.0',
    'sqlparse==0.2.3',
    'Tempita==0.5.2',
    'testpath==0.3',
    'tornado==4.5.1',
    'traitlets==4.3.2',
    'vine==1.1.4',
    'virtualenv==15.1.0',
    'wcwidth==0.1.7',
    'Werkzeug==0.12.1',
    'widgetsnbextension==2.0.0',
    'wincertstore==0.2',
    'WTForms==2.1'
]

setup(
    name="code_visualisationEV",
    version="0.1",
    description='code_visualisationEV',
    packages=find_packages(),
    zip_safe=False,
    install_requires=requires,
)
