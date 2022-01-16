"""
Constants
"""

# Directory where the result file will be stored
RESULT_FILE_PATH = r'C:\var'

# Wait time for Packet Stream handler till its in_queue gets some content
CONFIG_PKT_IN_WAIT_TIME = 1

# Wait time for Stream Resource handler till one of its in_queue or worker result queue gets some content
CONFIG_STREAM_IN_WAIT_TIME = 1

# Maximum number of workers to spawn to handle stream resource
CONFIG_MAX_PROCESS = 5
