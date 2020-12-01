import ujson
from flask import Blueprint, send_from_directory
from flask import current_app
from flask import request
from redis import Redis
from rq import Queue

from madrich.api.app.exceptions import InvalidUsage
from madrich.api.app.solver import run_solver, generate_random
from madrich.api.app.utils import save_file
from madrich.config import settings
from madrich.formats.excel.universal import StandardDataFormat
from madrich.formats.export import export_to_excel
from madrich.solvers.vrp_cli.generators import generate_mdvrp

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

    data = StandardDataFormat.from_excel_to_json(settings.UPLOAD_DIR / filename)
    return {"job_id": str(job_id), 'parsed_data': data}


@urls_blueprint.route('/random_task', methods=['POST'])
def random_genetic_solver_task():
    filename = 'random_example.xlsx'
    file = settings.UPLOAD_DIR / filename
    agents_list, jobs_list, depots_list = generate_mdvrp(20, 4, 10)
    StandardDataFormat.to_excel(agents_list, jobs_list, depots_list, file)

    redis_conn = Redis(current_app.config['RQ_REDIS_URL'])
    queue = Queue(connection=redis_conn)

    job = queue.enqueue(run_solver, filename)
    job_id = job.get_id()

    data = StandardDataFormat.from_excel_to_json(file)
    return {"job_id": str(job_id), 'parsed_data': data}


@urls_blueprint.route("/example")
def get_file_example():
    filename = 'random_example.xlsx'
    generate_random(filename)
    return send_from_directory(settings.UPLOAD_DIR, filename, as_attachment=True)


@urls_blueprint.route('/get_excel')
def get_excel(data):
    filename = 'generated_file.xlsx'
    file = settings.UPLOAD_DIR / filename
    export_to_excel(data, file)
    return send_from_directory(settings.UPLOAD_DIR, filename, as_attachment=True)
