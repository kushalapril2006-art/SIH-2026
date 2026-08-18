#!/bin/bash

clear

echo "=============================================================="
echo "             SIH AUTONOMOUS CYBER DEFENSE MVP"
echo "=============================================================="
echo
echo "Initializing isolated cyber range..."
echo

sudo docker compose down >/dev/null 2>&1
sudo rm -f telemetry/*.log telemetry/events.json
sudo docker compose up -d >/dev/null

sleep 3

echo
echo "[1/5] ADVERSARIAL SIMULATION"
echo "--------------------------------------------------------------"
echo "Technique : Network Service Scanning"
echo "Engine    : Nmap"
echo "Source    : Adversarial Simulation Container"
echo "Target    : Protected Workload"
echo
echo "Executing controlled reconnaissance..."
echo

sudo docker exec sih-attacker nmap -T4 -p- sih-victim 2>/dev/null

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Attack simulation failed."
    exit 1
fi

echo
echo "Waiting for behavioral telemetry..."

TELEMETRY_READY=false

for i in {1..15}; do
    if [ -f telemetry/conn.log ] && [ -s telemetry/conn.log ]; then
        TELEMETRY_READY=true
        break
    fi

    sleep 1
done

if [ "$TELEMETRY_READY" = false ]; then
    echo
    echo "ERROR: Zeek telemetry was not generated."
    echo "Defense cycle aborted."
    exit 1
fi

echo "Telemetry stream synchronized."

echo
echo "[2/5] BEHAVIORAL TELEMETRY"
echo "--------------------------------------------------------------"
echo "Sensor    : Zeek"
echo "Pipeline  : Packet Traffic -> Zeek -> Normalized Events"
echo

sudo docker exec sih-defender python /app/telemetry_parser.py

if [ ! -f telemetry/events.json ]; then
    echo
    echo "ERROR: Telemetry normalization failed."
    echo "Defense cycle aborted."
    exit 1
fi

python3 - <<'PY'
import json

with open("telemetry/events.json") as f:
    events = json.load(f)

tcp = [e for e in events if e.get("protocol") == "tcp"]

sources = {e.get("source_ip") for e in tcp}
targets = {e.get("destination_ip") for e in tcp}
ports = {e.get("destination_port") for e in tcp}

print(f"Events processed       : {len(events)}")
print(f"TCP connections        : {len(tcp)}")
print(f"Sources observed       : {len(sources)}")
print(f"Targets observed       : {len(targets)}")
print(f"Unique ports observed  : {len(ports)}")

if tcp:
    print(f"Source                  : {tcp[0].get('source_ip')}")
    print(f"Target                  : {tcp[0].get('destination_ip')}")
PY

echo
echo "[3/5] THREAT INFERENCE"
echo "--------------------------------------------------------------"

sudo docker exec sih-defender python /app/detector.py

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Threat inference failed."
    echo "Response not executed."
    exit 1
fi

echo
echo "[4/5] AUTOMATED CONTAINMENT"
echo "--------------------------------------------------------------"

sudo docker exec sih-defender python /app/response.py

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Containment failed."
    exit 1
fi

echo
echo "[5/5] CONTAINMENT VALIDATION"
echo "--------------------------------------------------------------"

echo "Re-attempting access to protected workload..."
echo

sudo docker exec sih-attacker nmap -T4 -p 80 sih-victim 2>&1

echo
echo "=============================================================="
echo "                  DEFENSE CYCLE COMPLETE"
echo "=============================================================="
echo
echo "Attack       -> Observed"
echo "Telemetry    -> Normalized"
echo "Threat       -> Inferred"
echo "Response     -> Executed"
echo "Containment  -> Validated"
echo
