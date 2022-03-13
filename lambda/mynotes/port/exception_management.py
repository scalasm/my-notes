import functools
from typing import Dict, Any

from mynotes.core.architecture import ApplicationException, ResourceNotFoundException, ValidationException
from mynotes.port.lambda_utils import to_json_response

INTERNAL_ERROR_CODE = "err-0000"
RESOURCE_NOT_FOUND_ERROR_CODE = "err-0001"
VALIDATION_ERROR_CODE = "err-0002"

def on_resource_not_found_exception(e: ResourceNotFoundException) -> Dict[str,Any]:
    return to_json_response(object_body={
        "error_message": f"Resource of type {e.resource_type} with id {e.resource_id} was not found!",
        "error_code": RESOURCE_NOT_FOUND_ERROR_CODE
    }, http_status_code=404)

def on_validation_exception(e: ValidationException) -> Dict[str,Any]:
    return to_json_response(object_body={
        "error_message": f"Invalid attribute {e.attribute_name}: {e.error_message}!",
        "error_code": VALIDATION_ERROR_CODE
    }, http_status_code=400)

def on_application_exception(e: ApplicationException) -> Dict[str,Any]:
    return to_json_response(object_body={
        "error_message": f"Internal error: {str(e)}!",
        "error_code": INTERNAL_ERROR_CODE
    }, http_status_code=500)

def with_exception_management(wrapped_function) -> Dict[str, Any]:
    @functools.wraps(wrapped_function)
    def translate_exception(*args, **kwargs) -> Dict[str, Any]:
        try:
            lambda_response = wrapped_function(*args, **kwargs)
        except ResourceNotFoundException as rnfe:
            lambda_response = on_resource_not_found_exception(rnfe)
        except ValidationException as ve:
            lambda_response = on_validation_exception(ve)
        except ApplicationException as ae:
            lambda_response = on_application_exception(ae)
        return lambda_response

    return translate_exception
