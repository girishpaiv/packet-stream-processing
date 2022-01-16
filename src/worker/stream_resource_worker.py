import json
import multiprocessing
import sys

from model.message_types import MessageType
from service.ancillary_service import AncillaryService


class StreamResourceWorker:
    """
    Worker class to handle a stream resource by calling the synchronous ancillary service
    """
    def __init__(self, stream_resource, out_queue):
        self.resource_id = stream_resource.resource_id
        self.stream_resource = stream_resource
        self.out_queue = out_queue
        self.proc = multiprocessing.Process(target=self.process_stream_resource, args=(stream_resource,))
        # print("LOG debug: StreamResourceWorker Init Complete!")
        # print("LOG debug:", self.__dict__)

    def process_stream_resource(self, stream_resource):
        """
        Pass the payload of each packet in the stream_resource to the AncillaryService
        and construct the result for that stream_resource
        :param stream_resource:
        :return:
        """
        res = []
        for pkt in stream_resource.packets_buffer:
            res.append(AncillaryService.convert_payload_to_array(pkt.payload))

        result_msg = {
            'type': MessageType.STREAM_RESOURCE_RESULT.value,
            'data': {
                'resource_id': self.resource_id,
                'result_array': res
            }
        }
        self.out_queue.put(result_msg)
        sys.exit()

    def start(self):
        self.proc.start()
