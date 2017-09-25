#critères de connexion à la base de données
dbName ='naturalite'
user='postgres'
host='localhost'
port=5432
password='perretho'

#connexion à la base de données
SQLALCHEMY_DATABASE_URI = 'postgresql://' + str(user) + ':' + str(password) + '@' + str(host) + ':' + str(port) + '/' + str(dbName)
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True

# critères de recherche des images sat
sunElevation = 70
cloudCoverage = 5
thresholdNDVI = 0.35
limitScene = 1
