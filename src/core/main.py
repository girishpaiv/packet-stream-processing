import json
import multiprocessing
import os
import random
import time

from libs.constants import RESULT_FILE_PATH
from model.message_types import MessageType
from service.packet_stream_handler_service import PacketStreamHandlerService


def construct_packets_to_stream(resources_count, packets_count):
    stream_pkts = []
    for res_id in range(1, resources_count+1):
        for pkt_id in range(1, packets_count+1):
            pkt_dict = {
                'type': MessageType.PACKET.value,
                'data': {
                    'resource_id': res_id,
                    'payload': f"pl {res_id} {pkt_id}",
                    'index': pkt_id,
                    'last_chunk_flag': True if pkt_id == packets_count else False
                }
            }
            stream_pkts.append(json.dumps(pkt_dict))

    random.shuffle(stream_pkts)
    # for pkt_json in stream_pkts:
    #     pkt = json.loads(pkt_json)
    #     print(pkt['data']['resource_id'], pkt['data']['index'])
    return stream_pkts


def test_packet_stream_service(packets_stream):
    # Initialize the Packer Stream service
    in_queue = multiprocessing.Queue()
    packet_stream_handler = PacketStreamHandlerService(in_queue)

    # Start the service
    packet_stream_handler.start_service()

    # Stream the packets one after the other
    for pkt_json in packets_stream:
        in_queue.put(pkt_json)

    # Trigger packer stream service to End
    end_msg = {'type': MessageType.EXIT.value}
    in_queue.put(json.dumps(end_msg))

    # Wait for the packet stream service to end
    packet_stream_handler.wait_to_end()


if __name__ == "__main__":
    resources_count = 40
    packets_count = 3
    pkts_stream = construct_packets_to_stream(resources_count, packets_count)
    for pkt_json in pkts_stream:
        pkt = json.loads(pkt_json)
        print(f"Test packet. Res Id: {pkt['data']['resource_id']}, Pkt Index: {pkt['data']['index']}")

    print("Initiating Test...")
    start_time = time.time()
    test_packet_stream_service(pkts_stream)
    print("--- done Test in %s seconds ---" % (time.time() - start_time))

    for res_id in range(1, resources_count+1):
        file_path = RESULT_FILE_PATH + '\\' + str(res_id)
        result_file = open(file_path)
        print(f"File {file_path} contents:\n", result_file.read())
        result_file.close()
        os.remove(file_path)
