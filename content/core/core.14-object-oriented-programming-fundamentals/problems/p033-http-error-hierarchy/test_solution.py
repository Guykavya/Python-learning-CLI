import pytest

from solution import AppError, NotFound, PermissionDenied, ValidationError, handle, status_for


def get_book(book_id):
    if book_id != 1:
        raise NotFound("book", book_id)
    return {"id": 1, "title": "Python"}


def test_hierarchy():
    assert issubclass(AppError, Exception), "AppError must inherit from Exception."
    for cls in (NotFound, ValidationError, PermissionDenied):
        assert issubclass(cls, AppError), f"{cls.__name__} must inherit from AppError, so one `except AppError` catches it."


def test_status_class_attributes():
    assert (AppError.status, NotFound.status, ValidationError.status, PermissionDenied.status) == (500, 404, 422, 403), (
        "Give each class a class attribute status: 500, 404, 422, 403."
    )


def test_base_message():
    err = AppError("disk full")
    assert str(err) == "disk full", "AppError(message): str(err) must give the message."


def test_not_found():
    err = NotFound("book", 42)
    assert (err.resource, err.key) == ("book", 42), "Store resource and key as attributes."
    assert str(err) == "book 42 not found", (
        "str(err) is empty or wrong: pass the message to the parent with super().__init__(message)."
    )
    assert str(NotFound("user", "asha")) == "user 'asha' not found", "Use {key!r} so a text key gets quotes."


def test_validation_error():
    err = ValidationError("email", "missing @")
    assert (err.field, err.problem) == ("email", "missing @"), "Store field and problem."
    assert str(err) == "email: missing @", "The message is 'field: problem'."


def test_permission_denied():
    err = PermissionDenied("ravi", "delete books")
    assert (err.user, err.action) == ("ravi", "delete books"), "Store user and action."
    assert str(err) == "ravi may not delete books", "The message is 'user may not action'."


def test_to_dict():
    assert NotFound("book", 7).to_dict() == {"error": "NotFound", "message": "book 7 not found", "status": 404}, (
        "to_dict uses the class name of the real object (type(self).__name__), str(self) and self.status."
    )
    assert AppError("x").to_dict() == {"error": "AppError", "message": "x", "status": 500}, "Works for the base class too."


def test_status_for():
    assert status_for(NotFound("a", 1)) == 404, "NotFound -> 404."
    assert status_for(ValidationError("f", "p")) == 422, "ValidationError -> 422."
    assert status_for(PermissionDenied("u", "a")) == 403, "PermissionDenied -> 403."
    assert status_for(AppError("x")) == 500, "AppError itself -> 500."
    assert status_for(KeyError("x")) == 500, "Any other exception -> 500."
    assert status_for(ValueError("x")) == 500, "Any other exception -> 500."


def test_status_for_future_subclasses():
    class Gone(NotFound):
        status = 410

    class MissingPage(NotFound):
        pass

    class Conflict(AppError):
        status = 409

    assert status_for(Gone("page", 3)) == 410, (
        "Read err.status instead of checking each class with isinstance; a new subclass may set its own status."
    )
    assert status_for(MissingPage("page", 3)) == 404, "A subclass without its own status inherits 404 from NotFound."
    assert status_for(Conflict("busy")) == 409, "A new AppError subclass brings its own status."


def test_handle_success():
    assert handle(get_book, 1) == (200, {"id": 1, "title": "Python"}), "On success return (200, result)."
    assert handle(lambda: None) == (200, None), "A function that returns None is still a success."
    assert handle(max, 3, 9, 4) == (200, 9), "Pass *args on to the function."


def test_handle_app_errors():
    assert handle(get_book, 7) == (404, {"error": "NotFound", "message": "book 7 not found", "status": 404}), (
        "An AppError becomes (err.status, err.to_dict()). Put `except AppError` before `except Exception`: the first matching clause wins."
    )

    def check_age(age):
        raise ValidationError("age", "must be a number")

    assert handle(check_age, "x") == (422, {"error": "ValidationError", "message": "age: must be a number", "status": 422})


def test_handle_unexpected_errors_hide_details():
    def broken():
        return {"a": 1}["password=secret"]

    status, body = handle(broken)
    assert status == 500, "Any other exception becomes status 500."
    assert body == {"error": "InternalError", "message": "internal server error", "status": 500}, (
        "Do not put the real message (it may contain secrets) in the body."
    )


def test_handle_does_not_swallow_keyboard_interrupt():
    def stop():
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        handle(stop)
