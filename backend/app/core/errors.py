class ApplicationError(Exception):
    status_code = 400

class NotFoundError(ApplicationError):
    status_code = 404

class PermissionDeniedError(ApplicationError):
    status_code = 403

class ServiceUnavailableError(ApplicationError):
    status_code = 503
