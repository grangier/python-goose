from flask import Flask
from flask import request
from flask import Response
from flask import redirect
from flask import url_for
from flask import render_template
from decorators import authenticate
from lib.goose_api import GooseAPI
import json
app = Flask(__name__)


@app.route("/")
def root():
    return redirect(url_for('swagger'))

@app.route("/api")
def api():
    pass # SwaggerUI helper URL

@app.route("/api/extract.json")
@authenticate.requires_auth
def extract():
    extracted_content = GooseAPI(request.args.get('url')).extract()
    return Response(json.dumps(extracted_content), mimetype='application/json')

@app.route('/swagger')
@authenticate.requires_auth
def swagger():
    return render_template('/api/documentation/show.html')

@app.route('/api/documentation/endpoints/<name>')
@authenticate.requires_auth
def documentation_endpoints(name=None):
    return render_template('/api/documentation/endpoints/%s' % name, mimetype='application/json')

@app.route('/api/documentation/<name>')
@authenticate.requires_auth
def documentation(name=None):
    return render_template('/api/documentation/%s.json' % name, mimetype='application/json')


if __name__ == "__main__":
    app.run(debug=False)
