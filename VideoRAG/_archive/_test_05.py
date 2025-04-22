# Test timer code

import os
import logging
import warnings
import time
from datetime import datetime, timedelta

def main():
    start_time = time.time()


    # Do some interesting things
    time.sleep(5) # Added a placeholder for some work

    end_time = time.time()
    run_time_seconds = end_time - start_time

    run_time_timedelta = timedelta(seconds=run_time_seconds)
    hours = run_time_timedelta.seconds // 3600
    minutes = (run_time_timedelta.seconds % 3600) // 60
    seconds = round(run_time_timedelta.seconds % 60)

    print(f"The script took {hours} hours, {minutes} minutes, and {seconds} seconds to run.")

if __name__ == "__main__":
    main()