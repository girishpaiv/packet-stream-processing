import json
import multiprocessing
import os
import sys
import time

from libs.constants import CONFIG_PKT_IN_WAIT_TIME, RESULT_FILE_PATH
from model.message_types import MessageType
from model.packet import Packet
from model.stream_resource import StreamResource
from service.stream_resource_handler_service import StreamResourceHandlerService


class PacketStreamHandlerService:
    """
    This class stores the context of each incoming Stream Resource Jobs and
    triggers the processing as and when each stream is ready with all it's packets.
    """
    def __init__(self, in_queue):
        """
        @param in_queue Queue to receive the raw incoming packets
        """
        self.in_queue = in_queue

        # Dict of PrimaryResourceID <-> StreamResource Object
        self.stream_resources_map = {}
        self.proc = multiprocessing.Process(target=self.run_service, args=())

        self.to_stream_processor_queue = multiprocessing.Queue()
        self.stream_resource_handler = StreamResourceHandlerService(self.to_stream_processor_queue, self.in_queue)

        print("LOG info: PacketStreamHandlerService Init Complete!\n", self.__dict__)
        # print("LOG info:", self.__dict__)

    def insert_to_stream_processor(self, stream_resource):
        self.to_stream_processor_queue.put(stream_resource)

    def handle_packet(self, packet_json):
        # print("LOG debug: PacketStreamHandlerService::handle_packet packet_json:!", packet_json)
        pkt = Packet(packet_json)
        if pkt.resource_id not in self.stream_resources_map:
            stream_resource = StreamResource(pkt.resource_id)
            self.stream_resources_map[pkt.resource_id] = stream_resource

        stream_resource = self.stream_resources_map[pkt.resource_id]
        stream_resource.insert_packet(pkt)

        # The Stream Resource has received all packets and is ready to be processed
        # print("LOG debug: Stream is ready to process:", stream_resource.is_ready_to_process())
        if stream_resource.is_ready_to_process():
            self.stream_resources_map.pop(pkt.resource_id)
            self.insert_to_stream_processor(stream_resource)

    @staticmethod
    def write_to_file(resource_result):
        resource_file = os.path.join(RESULT_FILE_PATH, str(resource_result['resource_id']))
        result_array = resource_result['result_array']
        # print(f"LOG debug: Writing result {result_array} for resource_id {resource_result['resource_id']} to file {file}")
        with open(resource_file, 'w') as file_handle:
            for pkt_result_array in result_array:
                for pkt_result in pkt_result_array:
                    file_handle.write(f'{pkt_result}\n')

    def run_service(self):
        while True:
            if self.in_queue.empty():
                time.sleep(CONFIG_PKT_IN_WAIT_TIME)
                continue
            msg = json.loads(self.in_queue.get())
            # print("LOG debug: PacketStreamHandlerService::run_service Received msg:", msg)
            if msg['type'] == MessageType.PACKET.value:
                packet_data = msg['data']
                self.handle_packet(packet_data)
            elif msg['type'] == MessageType.STREAM_RESOURCE_RESULT.value:
                # Handle the result for a resource
                self.write_to_file(msg['data'])
            if msg['type'] == MessageType.EXIT.value:
                self.insert_to_stream_processor("END")
            if msg['type'] == MessageType.CHILD_ENDED.value:
                self.close()
                sys.exit()

    def start_service(self):
        self.proc.start()
        self.stream_resource_handler.start_service()

    def close(self):
        self.stream_resources_map.clear()

    def wait_to_end(self):
        self.stream_resource_handler.wait_to_end()
        self.proc.join()
