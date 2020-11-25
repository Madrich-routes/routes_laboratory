from flask import Flask, jsonify
from flask_rq2 import RQ

from madrich.api.app.exceptions import InvalidUsage
from madrich.api.app.urls import urls_blueprint
from madrich.config import settings

app = Flask(__name__)
app.register_blueprint(urls_blueprint)
app.config['RQ_REDIS_URL'] = settings.REDIS_HOST
app.config['UPLOAD_FOLDER'] = settings.UPLOAD_DIR
rq_app = RQ(app)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
