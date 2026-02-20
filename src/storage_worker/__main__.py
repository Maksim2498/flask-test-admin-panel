import json
import logging
import sys
from argparse import ArgumentParser

import pika

from common.user.io.rpc_dispatch import dispatch_storage_rpc
from common.user.io.storage.rabbitmq_user_storage import DEFAULT_USER_STORAGE_RPC_QUEUE
from common.user.storage_factory import create_user_storage_backend

__all__ = ["main"]

_log = logging.getLogger(__name__)


def _build_parser() -> ArgumentParser:
  p = ArgumentParser(prog="storage_worker", description="User storage RPC worker (RabbitMQ)")
  p.add_argument(
    "--rabbitmq-url",
    default="amqp://guest:guest@localhost:5672/",
    help="AMQP URL",
  )
  p.add_argument(
    "--rpc-queue",
    default=DEFAULT_USER_STORAGE_RPC_QUEUE,
    help="Request queue name",
  )
  p.add_argument(
    "--internal-storage",
    choices=("pickle", "sqlite3", "postgres", "mongodb"),
    default="pickle",
    help="Backend storage used inside the worker",
  )
  p.add_argument("--pickle-storage-dirname", default="db.pickle")
  p.add_argument("--sqlite3-storage-filename", default="db.sqlite3")
  p.add_argument("--postgres-host", default="localhost")
  p.add_argument("--postgres-port", type=int, default=5432)
  p.add_argument("--postgres-db", default="admin_panel")
  p.add_argument("--postgres-user", default="admin")
  p.add_argument("--postgres-password", default="admin")
  p.add_argument("--mongodb-host", default="localhost")
  p.add_argument("--mongodb-port", type=int, default=27017)
  p.add_argument("--mongodb-db", default="admin_panel")
  p.add_argument("--mongodb-user", default="")
  p.add_argument("--mongodb-password", default="")
  return p


def main(argv: list[str] | None = None) -> None:
  logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
  args = _build_parser().parse_args(argv)

  storage = create_user_storage_backend(
    args.internal_storage,
    pickle_storage_dirname=args.pickle_storage_dirname,
    sqlite3_storage_filename=args.sqlite3_storage_filename,
    postgres_host=args.postgres_host,
    postgres_port=args.postgres_port,
    postgres_db=args.postgres_db,
    postgres_user=args.postgres_user,
    postgres_password=args.postgres_password,
    mongodb_host=args.mongodb_host,
    mongodb_port=args.mongodb_port,
    mongodb_db=args.mongodb_db,
    mongodb_user=args.mongodb_user,
    mongodb_password=args.mongodb_password,
  )

  connection = pika.BlockingConnection(pika.URLParameters(args.rabbitmq_url))
  channel = connection.channel()
  channel.queue_declare(queue=args.rpc_queue, durable=True)
  channel.basic_qos(prefetch_count=1)

  def on_request(ch, method, properties, body: bytes):
    try:
      request = json.loads(body.decode("utf-8"))
      result = dispatch_storage_rpc(storage, request)
      response = {"ok": True, "result": result}
    except Exception as e:
      _log.exception("RPC handler error")
      response = {"ok": False, "error": str(e)}

    reply_to = properties.reply_to
    if reply_to:
      ch.basic_publish(
        exchange="",
        routing_key=reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(response, default=str).encode("utf-8"),
      )
    ch.basic_ack(delivery_tag=method.delivery_tag)

  channel.basic_consume(queue=args.rpc_queue, on_message_callback=on_request)
  _log.info("Listening on queue %r (backend=%s)", args.rpc_queue, args.internal_storage)
  try:
    channel.start_consuming()
  finally:
    try:
      connection.close()
    except Exception:
      ...


if __name__ == "__main__":
  main(sys.argv[1:])
