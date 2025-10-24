import time


def loop():
    print("⏳ Waiting for tasks...")


if __name__ == "__main__":
    print("Cron started!")

    while True:
        loop()
        time.sleep(5)