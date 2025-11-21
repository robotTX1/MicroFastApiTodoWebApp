import contextvars

request_context = contextvars.ContextVar("request")