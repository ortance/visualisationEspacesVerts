# informations nécessaires à la connexion à la base de données
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:perretho@localhost:5432/naturalite'
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True

# critères de recherche des images sat
sunElevation = 70
cloudCoverage = 5
thresholdNDVI = 0.35
limitScene = 1
