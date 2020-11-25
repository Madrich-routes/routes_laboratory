import ujson
from flask import Blueprint, send_from_directory
from flask import current_app
from flask import request
from redis import Redis
from rq import Queue

from madrich.api.app.exceptions import InvalidUsage
from madrich.api.app.solver import run_solver, run_random, generate_random
from madrich.api.app.utils import save_file
from madrich.settings import UPLOAD_DIR

urls_blueprint = Blueprint('urls', __name__, )


@urls_blueprint.route('/')
def index():
    return 'Index Page'


@urls_blueprint.route('/status', methods=['GET'])
def status():
    try:
        redis_conn = Redis(current_app.config['RQ_REDIS_URL'])
        job_id = request.args.get('task_id', '')
        queue = Queue(connection=redis_conn)
    except ValueError as e:
        raise InvalidUsage('', payload={'task_id': '', 'is_finished': False, 'result': '', 'error': str(e)})

    job = queue.fetch_job(job_id)
    if job is None:
        raise InvalidUsage('', payload={'task_id': '', 'is_finished': False, 'result': '', 'error': 'No such job'})

    result, error = job.result, ''
    if result is not None and 'error' in result:
        error = result['reason']
        result = 'error'

    return ujson.dumps({'task_id': job_id, 'is_finished': job.is_finished, 'result': result, 'error': error})


@urls_blueprint.route('/solver', methods=['POST'])
def genetic_solver_task():
    filename = save_file(request, current_app.config['UPLOAD_FOLDER'])

    redis_conn = Redis(current_app.config['RQ_REDIS_URL'])
    queue = Queue(connection=redis_conn)

    job = queue.enqueue(run_solver, filename)
    job_id = job.get_id()

    return {"job_id": str(job_id)}


@urls_blueprint.route('/random_task', methods=['POST'])
def random_genetic_solver_task():
    redis_conn = Redis(current_app.config['RQ_REDIS_URL'])
    queue = Queue(connection=redis_conn)

    job = queue.enqueue(run_random)
    job_id = job.get_id()

    return {"job_id": str(job_id)}


@urls_blueprint.route("/example")
def get_file():
    filename = 'random_example.xlsx'
    generate_random(filename)
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)
