from typing import Any

from flask import render_template, request

from common.io.dialog import TextDialog
from common.util.type import get_all_typed_attrs_info

__all__ = ["WebDialog"]


class WebDialog(TextDialog):
  def get_attr_text(self, obj: Any, attr_name: str) -> str | None:
    return request.form.get(attr_name)

  def show(self, obj: Any, **kwargs: Any) -> str:
    attrs = get_all_typed_attrs_info(obj)

    for name, value in request.form.items():
      if name in attrs:
        attrs[name].value = value

    return render_template(
      "form.jinja",
      attrs=attrs,
      title=kwargs.get("title"),
      submit_text=kwargs.get("submit_text"),
    )
