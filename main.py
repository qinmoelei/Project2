# main.py
from node_manager import NodeManager
from data_manager import DataManager
import hashlib
import sys
import struct

sys.path.append(".")
from raid6 import *
from utils import *
from original_text import text1
def main():
    node_manager = NodeManager()
    node_manager.add_node(
        node_id=0,
        address="12.23.32.1",
        max_capacity=1e5,
        read_speed=100,
        write_speed=100,
    )
    node_manager.add_node(
        node_id=1,
        address="12.23.32.2",
        max_capacity=1e5,
        read_speed=100,
        write_speed=100,
    )
    node_manager.add_node(
        node_id=2,
        address="12.23.32.3",
        max_capacity=1e5,
        read_speed=100,
        write_speed=100,
    )
    node_manager.add_node(
        node_id=3,
        address="12.23.32.4",
        max_capacity=1e5,
        read_speed=100,
        write_speed=100,
    )
    node_manager.add_node(
        node_id=4,
        address="12.23.32.5",
        max_capacity=1e5,
        read_speed=100,
        write_speed=100,
    )
    node_manager.add_node(
        node_id=5,
        address="12.23.32.6",
        max_capacity=1e5,
        read_speed=100,
        write_speed=100,
    )
    node_manager.add_node(
        node_id=6,
        address="12.23.32.7",
        max_capacity=1e5,
        read_speed=100,
        write_speed=100,
    )
    node_manager.add_node(
        node_id=7,
        address="12.23.32.8",
        max_capacity=1e5,
        read_speed=100,
        write_speed=100,
    )
    datamanager = DataManager(node_manager=node_manager, raid_manager=RAID6())
    data = text1
    datamanager.distribute_data(data)

    # one data is missing
    print("one data is missing")
    datamanager.node_manager.get_node(3).simulate_failure()
    data_chunks, failure_nodes_id_list = datamanager.retrieve_data(0)
    text_data_chunk = data_chunks[:-2]
    text_data_chunk = [item for item in text_data_chunk if item is not None]
    text_missing = hex_chunks_to_string(text_data_chunk)
    print("missing text", text_missing)
    data_chunks, parity_chunk_p, parity_chunk_q = datamanager.rebuild_data(
        data_chunks, failure_nodes_id_list
    )
    for id in failure_nodes_id_list:
        datamanager.node_manager.handle_failure(id)
    datamanager.restore_data(data_chunks, parity_chunk_p, parity_chunk_q)
    data_chunks, failure_nodes_id_list = datamanager.retrieve_data(0)
    text_data_chunk = data_chunks[:-2]
    print("recover text", datamanager.reshow_text(text_data_chunk))



    # # P is missing
    # print("P is missing")
    # datamanager.node_manager.get_node(6).simulate_failure()
    # data_chunks, failure_nodes_id_list = datamanager.retrieve_data(0)
    # text_data_chunk = data_chunks[:-2]
    # text_data_chunk = [item for item in text_data_chunk if item is not None]
    # text_missing = hex_chunks_to_string(text_data_chunk)
    # print("missing text", text_missing)
    # data_chunks, parity_chunk_p, parity_chunk_q = datamanager.rebuild_data(
    #     data_chunks, failure_nodes_id_list
    # )
    # for id in failure_nodes_id_list:
    #     datamanager.node_manager.handle_failure(id)
    # datamanager.restore_data(data_chunks, parity_chunk_p, parity_chunk_q)
    # data_chunks, failure_nodes_id_list = datamanager.retrieve_data(0)
    # text_data_chunk = data_chunks[:-2]
    # print("recover text", datamanager.reshow_text(text_data_chunk))



    # # Q is missing
    # print("Q is missing")
    # datamanager.node_manager.get_node(7).simulate_failure()
    # data_chunks, failure_nodes_id_list = datamanager.retrieve_data(0)
    # text_data_chunk = data_chunks[:-2]
    # text_data_chunk = [item for item in text_data_chunk if item is not None]
    # text_missing = hex_chunks_to_string(text_data_chunk)
    # print("missing text", text_missing)
    # data_chunks, parity_chunk_p, parity_chunk_q = datamanager.rebuild_data(
    #     data_chunks, failure_nodes_id_list
    # )
    # for id in failure_nodes_id_list:
    #     datamanager.node_manager.handle_failure(id)
    # datamanager.restore_data(data_chunks, parity_chunk_p, parity_chunk_q)
    # data_chunks, failure_nodes_id_list = datamanager.retrieve_data(0)
    # text_data_chunk = data_chunks[:-2]
    # print("recover text", datamanager.reshow_text(text_data_chunk))



    # # Q and one data is missing
    # print("Q and one data are missing")
    # datamanager.node_manager.get_node(7).simulate_failure()
    # datamanager.node_manager.get_node(2).simulate_failure()
    # data_chunks, failure_nodes_id_list = datamanager.retrieve_data(0)
    # text_data_chunk = data_chunks[:-2]
    # text_data_chunk = [item for item in text_data_chunk if item is not None]
    # text_missing = hex_chunks_to_string(text_data_chunk)
    # print("missing text", text_missing)
    # data_chunks, parity_chunk_p, parity_chunk_q = datamanager.rebuild_data(
    #     data_chunks, failure_nodes_id_list
    # )
    # for id in failure_nodes_id_list:
    #     datamanager.node_manager.handle_failure(id)
    # datamanager.restore_data(data_chunks, parity_chunk_p, parity_chunk_q)
    # data_chunks, failure_nodes_id_list = datamanager.retrieve_data(0)
    # text_data_chunk = data_chunks[:-2]
    # print("recover text", datamanager.reshow_text(text_data_chunk))



    # # P and one data is missing
    # print("P and one data are missing")
    # datamanager.node_manager.get_node(6).simulate_failure()
    # datamanager.node_manager.get_node(2).simulate_failure()
    # data_chunks, failure_nodes_id_list = datamanager.retrieve_data(0)
    # print("data_chunks",data_chunks)
    # text_data_chunk = data_chunks[:-2]
    # text_data_chunk = [item for item in text_data_chunk if item is not None]
    # text_missing = hex_chunks_to_string(text_data_chunk)
    # print("missing text", text_missing)
    # data_chunks, parity_chunk_p, parity_chunk_q = datamanager.rebuild_data(
    #     data_chunks, failure_nodes_id_list
    # )
    # for id in failure_nodes_id_list:
    #     datamanager.node_manager.handle_failure(id)
    # datamanager.restore_data(data_chunks, parity_chunk_p, parity_chunk_q)
    # data_chunks, failure_nodes_id_list = datamanager.retrieve_data(0)
    # text_data_chunk = data_chunks[:-2]
    # print("recover text", datamanager.reshow_text(text_data_chunk))


    # # two data is missing
    # print("two data are missing")
    # datamanager.node_manager.get_node(2).simulate_failure()
    # datamanager.node_manager.get_node(3).simulate_failure()
    # data_chunks, failure_nodes_id_list = datamanager.retrieve_data(0)
    # text_data_chunk = data_chunks[:-2]
    # text_data_chunk = [item for item in text_data_chunk if item is not None]
    # text_missing = hex_chunks_to_string(text_data_chunk)
    # print("missing text", text_missing)
    # print("failure_nodes_id_list",failure_nodes_id_list)
    # data_chunks, parity_chunk_p, parity_chunk_q = datamanager.rebuild_data(
    #     data_chunks, failure_nodes_id_list
    # )
    # for id in failure_nodes_id_list:
    #     datamanager.node_manager.handle_failure(id)
    # datamanager.restore_data(data_chunks, parity_chunk_p, parity_chunk_q)
    # data_chunks, failure_nodes_id_list = datamanager.retrieve_data(0)
    # text_data_chunk = data_chunks[:-2]
    # print("recover text", datamanager.reshow_text(text_data_chunk))









if __name__ == "__main__":
    main()
