# from .client import get_langfuse_client


# class TraceSpan:
#     def __init__(self, root_span):
#         self.root = root_span
#         self.langfuse = get_langfuse_client()

#     def generation(
#         self,
#         *,
#         model: str,
#         input,
#         call_fn,
#         usage_fn=None,
#         cost_details=None,
#     ):
#         if not self.root or not self.langfuse:
#             return call_fn()

#         with self.root.start_as_current_observation(
#             as_type="generation",
#             name="model-generation",
#             model=model,
#             input=input,
#         ):
#             output = call_fn()

#             usage = usage_fn(output) if usage_fn else None

#             self.langfuse.update_current_generation(
#                 output={
#                     "role": "assistant",
#                     "content": output,
#                 },
#                 usage_details=usage,
#                 cost_details=cost_details,
#             )

#             return output
from time import time
from typing import Any, Dict
from langfuse import propagate_attributes


# ---------------------------------------------------------
# NO-OP SPAN
# ---------------------------------------------------------

class NoOpSpan:
    def generation(self, **kwargs):
        pass

    def end(self, **kwargs):
        pass


# ---------------------------------------------------------
# REAL LANGFUSE SPAN
# ---------------------------------------------------------

class TracedSpan:
    def __init__(self, client: Langfuse, name: str, input: Dict[str, Any]):
        self.client = client
        self.start_ts = time()

        # ✅ THIS is the most important line
        self._attr_ctx = propagate_attributes(
            user_id=_user_id,
            session_id=_session_id,
        )
        self._attr_ctx.__enter__()

        self._span_ctx = client.start_as_current_observation(
            as_type="span",
            name=name,
            input=input,
        )
        self._root = self._span_ctx.__enter__()

    def generation(self, *, model: str, input, output, usage=None, cost=None):
        with self.client.start_as_current_observation(
            as_type="generation",
            name="model-generation",
            model=model,
            input=input,
        ):
            self.client.update_current_generation(
                output=output,
                usage_details=usage,
                cost_details=cost,
            )

    def end(self):
        self._span_ctx.__exit__(None, None, None)
        self._attr_ctx.__exit__(None, None, None)
