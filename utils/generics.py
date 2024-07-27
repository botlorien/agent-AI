import time


def get_dummy():
    # Get the current time in seconds since the epoch
    timestamp = time.time()

    # Convert the timestamp to milliseconds
    dummy = int(timestamp * 1000)

    print(dummy)
    return dummy
