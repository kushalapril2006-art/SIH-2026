import json
from collections import defaultdict
from datetime import datetime

INPUT_FILE = "/telemetry/events.json"

PORT_THRESHOLD = 20
TIME_WINDOW = 5.0


def detect_port_scan():

    with open(INPUT_FILE, "r") as f:
        events = json.load(f)

    connections = defaultdict(list)

    for event in events:

        if event.get("protocol") != "tcp":
            continue

        source = event.get("source_ip")
        target = event.get("destination_ip")

        try:
            timestamp = float(event.get("timestamp"))
            port = int(event.get("destination_port"))

        except (ValueError, TypeError):
            continue

        connections[(source, target)].append({
            "timestamp": timestamp,
            "port": port
        })

    detection = None

    for (source, target), connection_list in connections.items():

        connection_list.sort(key=lambda x: x["timestamp"])

        for i in range(len(connection_list)):

            start = connection_list[i]["timestamp"]
            ports = set()
            total_connections = 0

            for j in range(i, len(connection_list)):

                current = connection_list[j]

                if current["timestamp"] - start > TIME_WINDOW:
                    break

                ports.add(current["port"])
                total_connections += 1

            if len(ports) >= PORT_THRESHOLD:

                detection = {
                    "source": source,
                    "target": target,
                    "unique_ports": len(ports),
                    "total_connections": total_connections,
                    "duration": connection_list[j]["timestamp"] - start
                }

                break

        if detection:
            break

    print()
    print("SECURITY EVENT")
    print("-" * 62)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if detection:

        unique_ports = detection["unique_ports"]
        total_connections = detection["total_connections"]
        duration = detection["duration"]

        if unique_ports >= 500:
            risk = "CRITICAL"
            confidence = "HIGH"

        elif unique_ports >= 100:
            risk = "HIGH"
            confidence = "HIGH"

        else:
            risk = "MEDIUM"
            confidence = "MEDIUM"

        assessment = (
            f"{unique_ports} distinct TCP ports were contacted "
            f"within {duration:.2f} seconds. "
            f"{total_connections} connection attempts were observed. "
        )

        if unique_ports >= 100:
            assessment += (
                "The volume and frequency of connection attempts "
                "are consistent with network service scanning."
            )

        else:
            assessment += (
                "The activity shows characteristics of network "
                "reconnaissance and warrants investigation."
            )

        print(f"{'Status':<22}: DETECTED")
        print(f"{'Timestamp':<22}: {timestamp}")
        print(f"{'Event':<22}: Network Service Scanning")
        print(f"{'Technique':<22}: MITRE ATT&CK T1046")
        print(f"{'Source':<22}: {detection['source']}")
        print(f"{'Target':<22}: {detection['target']}")
        print(f"{'Protocol':<22}: TCP")
        print(f"{'Unique ports':<22}: {unique_ports}")
        print(f"{'Connections observed':<22}: {total_connections}")
        print(f"{'Detection window':<22}: {duration:.2f} seconds")
        print(f"{'Risk level':<22}: {risk}")
        print(f"{'Confidence':<22}: {confidence}")

        print("-" * 62)
        print("Assessment")
        print("-" * 62)
        print(assessment)

    else:

        print(f"{'Status':<22}: NORMAL")
        print(f"{'Timestamp':<22}: {timestamp}")
        print(f"{'Event':<22}: No scanning activity detected")

    print("-" * 62)


if __name__ == "__main__":
    detect_port_scan()
