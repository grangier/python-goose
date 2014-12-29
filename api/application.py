from flask import Flask
from flask import request
from flask import Response
from decorators import authenticate
from lib.goose_api import GooseAPI
import json
app = Flask(__name__)


@app.route("/api/extract.json")
#@authenticate.requires_auth
def extract():
    extracted_content = GooseAPI(request.args.get('url')).extract()
    return Response(json.dumps(extracted_content), mimetype='application/json')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
