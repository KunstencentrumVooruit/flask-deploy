flask-deploy
============

# INSTALLATIE

clone repo in directory waar appontwikkeling zal gebeuren

> git clone https://github.com/KunstencentrumVooruit/flask-deploy.git

# USAGE

> cd flask-deploy

1. fab create

* Vraagt om naam directory die zal aangemaakt worden. Maakt directory aan op zelfde niveau als flask-deploy. 
* Creëert virtualenv met alle nodige pythonlibs voor flask & swagger
* kopieert template.py -> app.py

> running app: ./app.py

Browser: http://localhost:5003/apiv1/sensoren

