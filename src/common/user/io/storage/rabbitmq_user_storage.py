import json
import threading
import time
import uuid
from collections.abc import Iterable
from typing import Any, override

import pika

from common.io.storage import Storage
from common.user import User
from common.user.user_json import user_from_dict, user_to_dict

__all__ = ["RabbitmqUserStorage", "DEFAULT_USER_STORAGE_RPC_QUEUE"]


DEFAULT_USER_STORAGE_RPC_QUEUE = "admin_panel.user.storage.rpc"


class RabbitmqUserStorage(Storage[User]):
  """User storage backed by a remote worker over RabbitMQ (JSON RPC)."""

  __url: str
  __queue: str
  __timeout: float
  __lock: threading.Lock

  def __init__(
    self,
    url: str,
    queue: str = DEFAULT_USER_STORAGE_RPC_QUEUE,
    timeout: float = 30.0,
  ):
    super().__init__()
    self.__url = url
    self.__queue = queue
    self.__timeout = timeout
    self.__lock = threading.Lock()

  def __rpc(self, method: str, args: dict[str, Any]) -> Any:
    body = {"method": method, "args": args}
    payload = json.dumps(body).encode("utf-8")

    with self.__lock:
      conn = pika.BlockingConnection(pika.URLParameters(self.__url))
      try:
        ch = conn.channel()
        result = ch.queue_declare(queue="", exclusive=True, auto_delete=True)
        reply_queue = result.method.queue
        corr_id = str(uuid.uuid4())
        response_holder: list[bytes | None] = [None]

        def on_response(_ch, _method, props, body_b: bytes):
          if props.correlation_id == corr_id:
            response_holder[0] = body_b
            _ch.stop_consuming()

        ch.basic_consume(queue=reply_queue, on_message_callback=on_response, auto_ack=True)
        ch.basic_publish(
          exchange="",
          routing_key=self.__queue,
          properties=pika.BasicProperties(
            reply_to=reply_queue,
            correlation_id=corr_id,
            content_type="application/json",
            delivery_mode=2,
          ),
          body=payload,
        )

        deadline = time.monotonic() + self.__timeout
        while response_holder[0] is None and time.monotonic() < deadline:
          conn.process_data_events(time_limit=0.2)

        raw = response_holder[0]
        if raw is None:
          raise TimeoutError(f"RabbitMQ RPC timeout after {self.__timeout}s for {method}")

        data = json.loads(raw.decode("utf-8"))
        if not data.get("ok"):
          raise RuntimeError(data.get("error", "RPC error"))
        return data.get("result")
      finally:
        try:
          conn.close()
        except Exception:
          ...

  @override
  def persist(self, obj: User) -> int:
    new_id = int(self.__rpc("persist", {"user": user_to_dict(obj)}))
    obj._id = new_id
    return new_id

  @override
  def load(self, obj_id: int) -> User | None:
    raw = self.__rpc("load", {"id": obj_id})
    if raw is None:
      return None
    return user_from_dict(raw)

  @override
  def load_all_ids(self) -> Iterable[int]:
    ids = self.__rpc("load_all_ids", {})
    return ids if isinstance(ids, list) else list(ids)

  @override
  def count(self) -> int:
    return int(self.__rpc("count", {}))

  @override
  def delete(self, obj_id: int) -> bool:
    return bool(self.__rpc("delete", {"id": obj_id}))

  @override
  def delete_all(self) -> int:
    return int(self.__rpc("delete_all", {}))

  @override
  def load_all(self) -> Iterable[User]:
    raw = self.__rpc("load_all", {})
    if not isinstance(raw, list):
      raw = list(raw)
    return (user_from_dict(d) for d in raw)
