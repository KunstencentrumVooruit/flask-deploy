#!bin/python

from flask import Flask, Blueprint
from flask.ext.restplus import Api, Resource, fields, apidoc

app = Flask(__name__)
# PREFIX van de api -> http://SERVERNAME/<URL_PREFIX>
blueprint = Blueprint('api', __name__, url_prefix='/apiv1')
# CUSTOM CREATE van Api object ipv api = Api(blueprint, ui=False)
api = Api()
# manuele add van endpoint specs met path naar swagger.json, anders auto op /apiv1/swagger.json
# AANPASSEN PATH->swagger.json naar /<NAMESPACE>/swagger.json
api.add_resource(api.swagger_view(), '/sensoren/swagger.json', endpoint='specs', doc=False)
# !!! Blueprint is een soort app. Aangezien de routes gekoppeld zijn ad blueprint, moet deze geregistreerd worden, dus niet api.init_app(app, add_specs=False, ui=False)
# init Api
api.init_app(blueprint, add_specs=False, ui=False)

# NAMESPACE: AANPASSEN! Komt overeen met http://<SERVERNAME>/URL_PREFIX/<NAMESPACE>
ns = api.namespace('sensoren', description='Temperatuursensoren Koelcel & Diepvriescel')

# PATH NAAR SWAGGER (/<NAMESPACE>/swagger)
@blueprint.route('/sensoren/swagger/', endpoint='swagger')
def swagger_ui():
    return apidoc.ui_for(api)

################# EFFECTIEVE API GEDEELTE
# => http://<SERVERNAME>/URL_PREFIX/<NAMESPACE>/
@ns.route('/', endpoint='sensoren')
@api.doc(description='test')
class MyResource(Resource):
    def get(self):
        return "Hello!"

model = api.model('Model', {
    'temperatuur': fields.String,
})

# => http://<SERVERNAME>/URL_PREFIX/<NAMESPACE>/<ID>
@ns.route('/<id>', endpoint='sensoren-id')
@api.doc(params={'id': '1=koelcel - 2=diepvriescel'})
class dagklapperDag(Resource):
    @api.doc(description='Returns temperature')
    @api.response(200, 'Success', model)
    def get(self, id):
        return id

################# EINDE EFFECTIEVE API GEDEELTE

# Blueprint registreren voor main loop, anders niet opgepikt door uwsgi (dus ook de routes niet)
app.register_blueprint(blueprint)

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug='on', port=5003)
