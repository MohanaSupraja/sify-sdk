# from contextlib import contextmanager
# from langfuse import propagate_attributes


# @contextmanager
# def langfuse_context(user_id=None, session_id=None):
#     attrs = {}
#     if user_id:
#         attrs["user_id"] = user_id
#     if session_id:
#         attrs["session_id"] = session_id

#     if attrs:
#         with propagate_attributes(**attrs):
#             yield
#     else:
#         yield
# sify/aiplatform/observability/context.py

from contextlib import contextmanager
from langfuse import propagate_attributes


@contextmanager
def langfuse_context(*, user_id=None, session_id=None):
    attrs = {}
    if user_id:
        attrs["user_id"] = user_id
    if session_id:
        attrs["session_id"] = session_id

    if attrs:
        with propagate_attributes(**attrs):
            yield
    else:
        yield


