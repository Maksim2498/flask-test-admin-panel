from typing import Any, override

from common.io.dialog import TextDialog
from common.util.type import AttrInfo, get_all_typed_attrs_info, get_attr_info

__all__ = ["CliDialog"]


class CliDialog(TextDialog):
  @override
  def get_attr_text(self, obj: Any, attr_name: str) -> str | None:
    attr = get_attr_info(obj, attr_name)

    if attr is None:
      attr = AttrInfo(attr_name)

    prompt = f"{attr.display_name} ({attr.placeholder}): "

    return input(prompt)

  @override
  def show(self, obj: Any, **kwargs: Any):
    print("\n".join([f"{attr.display_name}: {attr.display_value}" for attr in get_all_typed_attrs_info(obj).values()]))
