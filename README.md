# SIH 2026 — Autonomous Cyber Defense Demo

A container-based cybersecurity demo built for **Smart India Hackathon (SIH) 2026**. It demonstrates a defense workflow: simulate network reconnaissance, collect telemetry, detect port-scanning behavior, and isolate the simulation container.

> This is an MVP for demonstration and experimentation in the included Docker lab.

## How it works

```text
Nmap scan → Zeek connection logs → Normalized JSON events
          → Rule-based scan detection → Docker network isolation
          → Follow-up connectivity check
```

1. **Simulate:** An Ubuntu container runs Nmap against an Nginx workload.
2. **Observe:** Zeek monitors the lab bridge and writes connection logs.
3. **Normalize:** A Python parser converts Zeek's tab-separated logs into JSON.
4. **Detect:** A Python detector identifies TCP activity reaching at least **20 distinct destination ports within 5 seconds**, grouped by source and target.
5. **Contain:** The response script disconnects `sih-attacker` from the lab network.
6. **Inspect:** A second scan attempts to reach the workload after isolation.

The detector labels the event as Network Service Scanning (MITRE ATT&CK T1046) and prints a risk level, confidence label, and assessment. These are rule-based labels; the demo does not use a trained machine-learning model.

## Components

| Component | Role |
| --- | --- |
| `sih-victim` | Nginx workload used as the scan target |
| `sih-attacker` | Ubuntu container with Nmap, curl, and ping |
| `sih-zeek` | Network sensor monitoring the `sih-br` bridge |
| `sih-defender` | Python 3.12 container for parsing, detection, and response |

The attacker, victim, and defender share an internal Docker bridge network. Zeek uses host networking to observe the bridge. The defender accesses the Docker socket to perform network isolation.

## Requirements

- A **Linux host** with Docker Engine and the Docker Compose plugin.
- Bash, Git, Python 3, and `sudo` on the host.
- Internet access for the initial image downloads and builds.

The current configuration relies on a Linux bridge named `sih-br` and host networking. Windows and macOS Docker Desktop setups may require networking changes.

## Run the demo

Clone into a directory named **`sih`** so Docker Compose creates the `sih_cyberlab` network expected by `defender/response.py`:

```bash
git clone https://github.com/kushalapril2006-art/SIH-2026.git sih
cd sih

mkdir -p telemetry
sudo docker compose build
sudo docker compose pull victim zeek

bash demo.sh
```

If you use a different directory name, add `COMPOSE_PROJECT_NAME=sih` to a `.env` file in the repository root before running Compose or the demo.

**Each run resets the lab:** `demo.sh` stops the Compose services, deletes existing `telemetry/*.log` files and `telemetry/events.json`, then starts the services again.

### What to look for

The script displays five stages:

- **Adversarial simulation:** the initial Nmap scan.
- **Behavioral telemetry:** event counts and observed sources, targets, and ports.
- **Threat inference:** a `DETECTED` or `NORMAL` result and any scan assessment.
- **Automated containment:** an `ISOLATED` response when disconnection succeeds.
- **Containment validation:** a follow-up attempt to access port 80.

After isolation, the attacker should no longer reach the victim through the lab network. The follow-up command may report a name-resolution or connectivity failure; inspect its output rather than relying only on the script's completion banner.

## Generated telemetry

| File | Contents |
| --- | --- |
| `telemetry/conn.log` | Zeek connection records |
| `telemetry/events.json` | Normalized events consumed by the detector |

Normalized events include timestamps, source and destination addresses and ports, protocol, duration, byte counts, and connection state.

## Repository structure

```text
.
├── attacker/
│   └── Dockerfile
├── defender/
│   ├── Dockerfile
│   ├── telemetry_parser.py
│   ├── detector.py
│   └── response.py
├── demo.sh
├── docker-compose.yml
└── telemetry/                 # Created locally for runtime logs
```

## Troubleshooting

**No Zeek telemetry generated**

Inspect the sensor logs and confirm the lab bridge exists:

```bash
sudo docker compose logs zeek
ip link show sih-br
```

The script waits up to 15 seconds for a nonempty `conn.log` after the initial scan. Sensor startup, capture permissions, and log flushing can affect availability.

**Network not found during containment**

The response script uses the fixed name `sih_cyberlab`. Confirm the Compose project name is `sih` and inspect the available networks:

```bash
sudo docker network ls
```

**Inspect or stop the lab**

```bash
sudo docker compose ps
sudo docker compose logs
sudo docker compose down
```

## Current limitations

- Detection covers a specific TCP port-scanning pattern using fixed thresholds.
- The detector prints its result; it does not pass a structured decision to the response script. The demo invokes containment whenever the detector exits successfully, including when it prints `NORMAL`.
- Containment targets the fixed `sih-attacker` container rather than resolving a container from the detected source IP.
- The final scan is a visual check. The script does not automatically assert that isolation succeeded, and some response errors are printed without a failing exit status.
- The Docker socket gives the defender powerful control over the host's Docker daemon. Run this demo in a dedicated, trusted lab environment.

## Author

Created by [kushalapril2006-art](https://github.com/kushalapril2006-art) as a demo for **SIH 2026**.
