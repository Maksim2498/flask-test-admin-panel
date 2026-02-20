__all__ = ["BadJsonSchemaError"]


class BadJsonSchemaError(RuntimeError):
  def __init__(self):
    super().__init__("Bad JSON schema")
