import json
import builtins as __builtin__


def print(*args, **kwargs):
    if isinstance(args[0], dict):
        return __builtin__.print(json.dumps(args[0], sort_keys=True, indent=4))
    else:
        return __builtin__.print(*args, **kwargs)


def convert_to_seconds(time_str):
    # Split the string into hours, minutes, seconds, and microseconds
    hours, minutes, seconds_microseconds = time_str.split(':')

    # Convert each part to an integer
    hours = float(hours)
    minutes = float(minutes)
    seconds_microseconds = float(seconds_microseconds)

    # Calculate total seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds_microseconds

    return total_seconds
