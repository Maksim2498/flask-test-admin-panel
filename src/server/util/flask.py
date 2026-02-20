from typing import Any

from flask import render_template

from common.util.type import get_all_typed_attrs_info

__all__ = ["render_object"]


def render_object(obj: Any) -> str:
  return render_template("object.jinja", attrs=get_all_typed_attrs_info(obj))
