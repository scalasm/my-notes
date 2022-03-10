import pytest

from mynotes.core.architecture import wrap_exceptions, ApplicationException

@wrap_exceptions
def function() -> None:
    print("A function without any problem")

@wrap_exceptions
def function_with_exception() -> None:
    print("A function that throws an exception!")
    raise Exception("Catch me!")

def test_exception_is_wrapped() -> None:
    with pytest.raises(ApplicationException):
        function_with_exception()

def test_normal_execution_if_no_exception() -> None:
    function()

    assert True