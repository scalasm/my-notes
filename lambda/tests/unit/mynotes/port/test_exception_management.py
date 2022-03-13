from cmath import exp
import pytest
import json
from typing import Any

from mynotes.port.exception_management import (
    INTERNAL_ERROR_CODE,
    RESOURCE_NOT_FOUND_ERROR_CODE,
    VALIDATION_ERROR_CODE,
    on_application_exception,
    on_resource_not_found_exception,
    on_validation_exception,
    with_exception_management
)

from mynotes.core.architecture import ApplicationException, ResourceNotFoundException, ValidationException

on_error_handler_test_data = [
    (on_resource_not_found_exception, ResourceNotFoundException("resource-type", "id"), 404, RESOURCE_NOT_FOUND_ERROR_CODE, "was not found"),
    (on_validation_exception, ValidationException("attribute-1", "Something"), 400, VALIDATION_ERROR_CODE, "Invalid attribute"),
    (on_application_exception, ApplicationException("Whops!"), 500, INTERNAL_ERROR_CODE, "Internal error")
]

@pytest.mark.parametrize("handler_function,e,expected_http_code,expected_error_code,expected_error_message", on_error_handler_test_data)
def test_on_error_handler(handler_function: Any, e: ApplicationException, expected_http_code: int,expected_error_code: str, expected_error_message: str) -> None:
    lambda_response = handler_function(e)
    
    assert lambda_response["statusCode"] == expected_http_code
    response_body = json.loads(lambda_response["body"])
    assert response_body["error_code"] == expected_error_code
    assert expected_error_message in response_body["error_message"]

@with_exception_management
def function_throwing_resource_not_found_exception() -> None:
    raise ResourceNotFoundException("resource-type", "resource-id")

@with_exception_management
def function_throwing_validation_exception() -> None:
    raise ValidationException("some-attribute", "very bad error")

@with_exception_management
def function_throwing_application_exception() -> None:
    raise ApplicationException("Whops!")

with_exception_management_test_data = [
    (function_throwing_resource_not_found_exception, RESOURCE_NOT_FOUND_ERROR_CODE),
    (function_throwing_validation_exception, VALIDATION_ERROR_CODE),
    (function_throwing_application_exception, INTERNAL_ERROR_CODE)
]

@pytest.mark.parametrize("function,expected_error_code", with_exception_management_test_data)
def test_with_exception_management(function: Any, expected_error_code: str) -> None:
    lambda_response = function()

    response_body = json.loads(lambda_response["body"])

    assert response_body["error_code"] == expected_error_code
