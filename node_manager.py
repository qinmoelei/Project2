import random
import socket
import os
import pickle


class StorageNode:
    def __init__(
        self,
        id,
        address,
        max_capacity,
        read_speed,
        write_speed,
        simluated_file_path="nodes",
    ):
        self.id = id
        self.address = address
        self.max_capacity = max_capacity  # 节点的最大存储容量
        self.used_capacity = 0  # 当前已使用的容量
        self.read_speed = read_speed  # 单位：MB/s
        self.write_speed = write_speed  # 单位：MB/s
        self.online = True
        self.stored_data = []
        self.start_index_list = [0]
        self.file_path = simluated_file_path
        if not os.path.exists(os.path.join(self.file_path, address)):
            os.makedirs(os.path.join(self.file_path, address))
        self.stored_path = os.path.join(self.file_path, address)

    def set_online(self, status):
        self.online = status

    def is_online(self):
        return self.online

    def simulate_failure(self):
        """模拟节点故障，用于测试"""
        self.set_online(False)
        self.stored_data = []
        self.start_index_list = [0]
        with open(os.path.join(self.stored_path, "hex_data.bin"), "wb") as file:
            pickle.dump(self.stored_data, file)

    def store_data(self, data_chunk):
        """模拟存储数据并计算所需时间"""
        if self.online == False:
            return False, 0
        if self.used_capacity + len(data_chunk) > self.max_capacity:
            print(f"Node {self.id} is out of capacity.")
            return False, 0
        self.used_capacity += len(data_chunk)
        time_taken = len(data_chunk) / self.write_speed  # 计算写入所需时间
        if len(self.stored_data) != 0:
            self.start_index_list.append(len(self.stored_data))
        for data in data_chunk:
            self.stored_data.append(data)
        with open(os.path.join(self.stored_path, "hex_data.bin"), "wb") as file:
            pickle.dump(self.stored_data, file)

        return True, time_taken

    def retrieve_data(self, index):
        with open(os.path.join(self.stored_path, "hex_data.bin"), "rb") as file:
            hex_chunks = pickle.load(file)
        self.stored_data = hex_chunks
        """模拟检索数据并计算所需时间"""
        if index > len(self.start_index_list) - 1:
            print(" there is no such index when store data")
            return False, None, 0
        if index == len(self.start_index_list) - 1:
            data_chunk = self.stored_data[self.start_index_list[index] :]
        else:
            data_chunk = self.stored_data[
                self.start_index_list[index] : self.start_index_list[index + 1]
            ]
        time_taken = len(data_chunk) / self.read_speed
        # 计算读取所需时间
        return True, data_chunk, time_taken


class NodeManager:
    def __init__(self):
        self.nodes = []

    def add_node(self, node_id, address, max_capacity, read_speed, write_speed):
        """添加新的存储节点，考虑读写速度和容量"""
        new_node = StorageNode(node_id, address, max_capacity, read_speed, write_speed)
        self.nodes.append(new_node)
        print(f"Node {node_id} added with address {address}")

    # 现有方法保持不变...
    def get_num_nodes(self):
        return len(self.nodes)
    
    def get_failutre_nodes(self):
        failure_nodes_id = []
        for node in self.nodes:
            if node and not node.is_online():
                failure_nodes_id.append(node.id)
        return failure_nodes_id


    def check_node_health(self):
        failure_nodes_id = []
        """检查每个节点的健康状况"""
        for node in self.nodes:
            self.report_status(node)
            if node.is_online() == False:
                failure_nodes_id.append(node.id)
        return failure_nodes_id

    def handle_failure(self, node_id):
        """处理节点故障的逻辑"""
        node = self.get_node(node_id)
        if node and not node.is_online():
            print(f"Handling failure of node {node_id}.")
            node.set_online(True)
            if not os.path.exists(os.path.join(node.stored_path, "hex_data.bin")):
                with open(os.path.join(node.stored_path, "hex_data.bin"), "wb") as file:
                    pickle.dump([], file)
            # 在这里实现故障处理逻辑，如重新分配数据等


    def get_node(self, id):
        """根据ID获取存储节点"""
        for node in self.nodes:
            if node.id == id:
                return node
        return None

    def report_status(self, node):
        """报告节点的状态"""
        status = "online" if node.is_online() else "offline"
        print(f"Node {node.id} is currently {status}.")

    def store_data_on_node(self, node_id, data_chunk):
        """在指定节点上存储数据，并返回所需时间"""
        node = self.get_node(node_id)
        if node and node.is_online():
            success, time_taken = node.store_data(data_chunk)
            return success, time_taken
        else:
            print("node is not online")
        return False, 0

    def retrieve_data_from_node(self, node_id, index):
        """从指定节点检索数据，并返回所需时间"""
        node = self.get_node(node_id)
        if node and node.is_online():
            success, data, time_taken = node.retrieve_data(index)
            return success, data, time_taken
        return False, None, 0
