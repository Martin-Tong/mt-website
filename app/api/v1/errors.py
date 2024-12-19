from flask import jsonify


class UserValidateError(Exception):
    pass

def unauthorized(data):
    response = jsonify({'message': '用户未登录', 'data': data})
    response.status_code = 401
    return response

def forbidden(data):
    response = jsonify({'message': '用户禁止登录或没有使用权限', 'data': data})
    response.status_code = 403
    return response

def something_wrong(data):
    response = jsonify({'message': '参数错误', 'data': data})
    response.status_code = 400
    return response

def error_404(data):
    response = jsonify({'message': '404', 'data': data})
    response.status_code = 404
    return response