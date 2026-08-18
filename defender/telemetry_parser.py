import json
from pathlib import Path

LOG_FILE = Path("/telemetry/conn.log")
OUTPUT_FILE = Path("/telemetry/events.json")


def parse_zeek_log():
    fields = None
    events = []

    with LOG_FILE.open("r", errors="ignore") as f:
        for line in f:
            line = line.rstrip()

            if line.startswith("#fields"):
                fields = line.split("\t")[1:]
                continue

            if line.startswith("#"):
                continue

            if not fields:
                continue

            values = line.split("\t")

            if len(values) != len(fields):
                continue

            event = dict(zip(fields, values))

            clean_event = {
                "timestamp": event.get("ts"),
                "source_ip": event.get("id.orig_h"),
                "source_port": event.get("id.orig_p"),
                "destination_ip": event.get("id.resp_h"),
                "destination_port": event.get("id.resp_p"),
                "protocol": event.get("proto"),
                "duration": event.get("duration"),
                "orig_bytes": event.get("orig_bytes"),
                "resp_bytes": event.get("resp_bytes"),
                "connection_state": event.get("conn_state"),
            }

            events.append(clean_event)

    with OUTPUT_FILE.open("w") as f:
        json.dump(events, f, indent=2)

    print(f"[+] Parsed {len(events)} network events")
    print(f"[+] Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    parse_zeek_log()
