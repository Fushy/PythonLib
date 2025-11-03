import os
import sys
import time
from datetime import datetime, timedelta

from peewee import CharField, DateTimeField, Model, PostgresqlDatabase

from Files import get_running_python_scripts
from Introspection import frameinfo
from Telegrams import message
from Times import now

dbname = "Base"
user = "postgres"
password = "ale"
db = PostgresqlDatabase(dbname, user=user, password=password, host='localhost')
db.connect()


class Ping(Model):
    name = CharField()
    ping = DateTimeField(null=True)
    start = DateTimeField(null=True)
    end = DateTimeField(null=True)

    class Meta:
        database = db
        table_name = 'Ping'


def ping(name=None, end=timedelta(minutes=1), start=False, debug=False):
    """
    Updates the 'ping' field with the current datetime. If 'end' is provided,
    it can be a timedelta (added to the current time), a datetime, or None.

    Parameters:
        end (timedelta | datetime | None): The time to set for 'end'.
            - If timedelta, it is added to the current time.
            - If datetime, it is used directly.
            - If None, the 'end' field is unchanged.
    """
    if not is_ping_running():
        print("ping.py is not running", frameinfo(1)["pathname"], file=sys.stderr)
    ping_name = os.path.basename(sys.argv[0]) if name is None else name
    record, created = Ping.get_or_create(name=ping_name)
    record.ping = now()
    if start:
        record.start = record.ping
    if isinstance(end, timedelta):
        record.end = now() + end
    elif isinstance(end, datetime):
        record.end = end
    record.save()
    if debug:
        if record.end:
            print(f"Ping update {ping_name} <{record.ping} - {str(record.end) if record.end else ''}>")
        else:
            print(f"Ping update {ping_name} <{record.ping}>")


def check_pings():
    for row in Ping.select():
        assert row.end
        print("ping check", row.name, str(now(with_ms=False).time()), str(row.end.time().replace(microsecond=0)))
        if now() < row.end:
            continue
        else:
            message(f"[PING] {row.name}, ({str(now(with_ms=False).time())}) >= ({str(row.end.time().replace(microsecond=0))}).")
            time.sleep(2)

def is_ping_running():
    return any(f"{os.sep}ping.py" in script_name for script_name in get_running_python_scripts())

# ping(end=timedelta(minutes=2), start=False)
if __name__ == "__main__":
    db.drop_tables([Ping])
    db.create_tables([Ping], safe=True)
    while True:
        check_pings()
        time.sleep(10)
