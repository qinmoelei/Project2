# RAID-6 Distributed Storage System Project

## Overview
This project implements a simple RAID-6 based distributed storage system in Python. It demonstrates the basic concepts of data striping, mirroring, and fault tolerance in a RAID-6 setup.

## Structure
- `main.py`: The entry point of the program, where we can set up various number of nodes(at least 4) for the RAID6
- `node_manager.py`: Manages the storage nodes, including storing data, calculating the time taken for read and write and failure simulation.
- `data_manager.py`: Handles the distribution and retrieval of data, including RAID6 mapping, transferring data type and retrive data.
- `raid6.py`: Implements RAID-6 encoding, decoding and recovering logic.
- `utils.py`: Provides utility functions like logging.

## Setup and Running
`pip -r requirements.txt` to install the development environment
## Testing
Run `python main.py` to see how the RAID6 can help covering different kinds of loss in data.

