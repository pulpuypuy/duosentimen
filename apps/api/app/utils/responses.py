from flask import jsonify


def ok(data=None, message: str = 'success', status: int = 200):
    return jsonify({'status': 'success', 'message': message, 'data': data}), status


def created(data=None, message: str = 'created'):
    return ok(data, message, 201)


def error(message: str = 'error', status: int = 400, details=None):
    body = {'status': 'error', 'message': message}
    if details:
        body['details'] = details
    return jsonify(body), status


def not_found(resource: str = 'Resource'):
    return error(f'{resource} tidak ditemukan', 404)


def unauthorized(msg: str = 'Unauthorized'):
    return error(msg, 401)


def server_error(msg: str = 'Internal server error'):
    return error(msg, 500)
