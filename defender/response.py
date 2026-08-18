import docker
from datetime import datetime

ATTACKER_CONTAINER = "sih-attacker"
NETWORK_NAME = "sih_cyberlab"


def isolate_attacker():
    client = docker.from_env()

    attacker = client.containers.get(ATTACKER_CONTAINER)
    network = client.networks.get(NETWORK_NAME)

    print()
    print("RESPONSE ACTION")
    print("-" * 62)

    try:
        network.disconnect(attacker)

        print(f"{'Status':<22}: ISOLATED")
        print(f"{'Container':<22}: {ATTACKER_CONTAINER}")
        print(f"{'Network':<22}: {NETWORK_NAME}")
        print(f"{'Action':<22}: Network access revoked")
        print(
            f"{'Timestamp':<22}: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        print("-" * 62)
        print("Response completed successfully.")
        print()

    except Exception as e:
        print(f"{'Status':<22}: FAILED")
        print(f"{'Reason':<22}: {e}")
        print("-" * 62)


if __name__ == "__main__":
    isolate_attacker()
