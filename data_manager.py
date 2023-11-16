import hashlib
import sys
import struct

sys.path.append(".")
from node_manager import NodeManager
from raid6 import *
from utils import *
from original_text import text


# 这里面主要做data mapping 并设置一共0-n-1个节点  n-2和n-1个节点为parity node 剩下的纯纯数据node
class DataManager:
    def __init__(self, node_manager: NodeManager, raid_manager: RAID6):
        self.node_manager = node_manager
        self.raid_manager = raid_manager
        self.num_node = node_manager.get_num_nodes()

    def distribute_data(self, data):
        """将数据分割并分配到不同的存储节点"""
        chunks = self.split_data(data)
        for i, chunk in enumerate(chunks):
            node = self.node_manager.get_node(i % (len(self.node_manager.nodes) - 2))
            if node and node.is_online():
                self.store_data_on_node(node, chunk)
        parity_chunk_p, parity_chunk_q = self.raid_manager.encode_data(chunks)
        self.store_data_on_node(
            self.node_manager.get_node(self.num_node - 2), parity_chunk_p
        )
        self.store_data_on_node(
            self.node_manager.get_node(self.num_node - 1), parity_chunk_q
        )

    def restore_data(self, datachunks, parity_chunk_p, parity_chunk_q):
        for i, chunk in enumerate(datachunks):
            node = self.node_manager.get_node(i % (len(self.node_manager.nodes) - 2))
            if node and node.is_online():
                self.store_data_on_node(node, chunk)
        self.store_data_on_node(
            self.node_manager.get_node(self.num_node - 2), parity_chunk_p
        )
        self.store_data_on_node(
            self.node_manager.get_node(self.num_node - 1), parity_chunk_q
        )

    def split_data(self, data):
        """将数据分割成小块，准备分布到各个节点"""
        # 根据需求实现数据分割逻辑
        # 例如，可以按照固定大小分割数据
        return string_to_hex_chunks(data, self.num_node)

    def store_data_on_node(self, node, data):
        """在指定节点存储数据块"""
        # 实现数据存储逻辑
        # 例如，可以通过网络调用将数据发送到节点
        node.store_data(data)

    def retrieve_data(self, index):
        """从存储节点中检索数据"""
        # 实现数据检索逻辑
        # 需要从多个节点收集数据块，并重新组合成原始数据
        data_chunks = []
        failure_nodes_id_list = []
        for node in self.node_manager.nodes:
            if node.is_online():
                success, data, time = node.retrieve_data(index)
                if data:
                    data_chunks.append(data)
            else:
                failure_nodes_id_list.append(node.id)
                data_chunks.append(None)
        return data_chunks, failure_nodes_id_list

    def rebuild_data(self, data_chunks, failure_nodes_id_list):
        """在节点故障时重建丢失的数据"""
        # 使用RAID-6的冗余信息来重建数据
        # 需要从其他节点收集数据和校验块
        parity_chunk_p = data_chunks[self.num_node - 2]
        parity_chunk_q = data_chunks[self.num_node - 1]
        data_chunks = data_chunks[:-2]
        if len(failure_nodes_id_list) == 0:
            return data_chunks, parity_chunk_p, parity_chunk_q
        if len(failure_nodes_id_list) == 1:
            if failure_nodes_id_list[0] == self.num_node - 1:
                parity_chunk_q = self.raid_manager.recover_data(
                    data_chunks,
                    parity_chunk_p,
                    parity_chunk_q,
                    "missing_Q",
                    failure_nodes_id_list,
                )
            elif failure_nodes_id_list[0] == self.num_node - 2:
                parity_chunk_p = self.raid_manager.recover_data(
                    data_chunks,
                    parity_chunk_p,
                    parity_chunk_q,
                    "missing_P",
                    failure_nodes_id_list,
                )
            elif failure_nodes_id_list[0] < self.num_node - 2:
                data_chunks = self.raid_manager.recover_data(
                    data_chunks,
                    parity_chunk_p,
                    parity_chunk_q,
                    "missing_one_data",
                    failure_nodes_id_list,
                )
        elif len(failure_nodes_id_list) == 2:
            failure_nodes_id_list.sort()
            if (failure_nodes_id_list[0] < self.num_node - 2) and (
                failure_nodes_id_list[1] == self.num_node - 1
            ):
                parity_chunk_q, data_chunks = self.raid_manager.recover_data(
                    data_chunks,
                    parity_chunk_p,
                    parity_chunk_q,
                    "missing_one_data_one_Q",
                    failure_nodes_id_list,
                )
            elif (failure_nodes_id_list[0] < self.num_node - 2) and (
                failure_nodes_id_list[1] == self.num_node - 2
            ):
                
                parity_chunk_p, data_chunks = self.raid_manager.recover_data(
                    data_chunks,
                    parity_chunk_p,
                    parity_chunk_q,
                    "recover_one_data_one_P",
                    failure_nodes_id_list,
                )
            elif (failure_nodes_id_list[0] < self.num_node - 2) and (
                failure_nodes_id_list[1] < self.num_node - 2
            ):
                data_chunks = self.raid_manager.recover_data(
                    data_chunks,
                    parity_chunk_p,
                    parity_chunk_q,
                    "recover_two_data",
                    failure_nodes_id_list,
                )
            else:
                print("there is something wrong with the failure node list")
        else:
            print("we could not handle such failure")
        return data_chunks, parity_chunk_p, parity_chunk_q

    def reshow_text(self, data_chunks):
        return hex_chunks_to_string(data_chunks)









