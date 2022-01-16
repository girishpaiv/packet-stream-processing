import json
import multiprocessing
import sys
import time

from libs.constants import CONFIG_MAX_PROCESS, CONFIG_STREAM_IN_WAIT_TIME
from model.message_types import MessageType
from worker.stream_resource_worker import StreamResourceWorker


class StreamResourceHandlerService:
    """
    This Service receives the Stream resources that are ready to be processed
    in the in_queue and spawn a worker per the stream resource to invoke the
    ancillary service to process the payload.
    """
    def __init__(self, in_queue, out_queue):
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.worker_result_queue = multiprocessing.Queue()
        self.max_process = CONFIG_MAX_PROCESS

        self.proc = multiprocessing.Process(target=self.run_service, args=())
        # Map of PrimaryResourceID <-> StreamResourceHandler Worker
        self.active_workers = {}
        # print("LOG debug: StreamResourceHandlerService Init!")
        # print("LOG debug:", self.__dict__)

    def invoke_stream_resource_worker(self, stream_resource):
        # print("LOG debug: StreamResourceHandlerService Invoking Worker for resource: ", stream_resource.resource_id)
        worker = StreamResourceWorker(stream_resource, self.worker_result_queue)
        worker.start()
        self.active_workers[stream_resource.resource_id] = worker

    def run_service(self):
        while True:
            if not self.in_queue.empty():
                free_procs = self.max_process - len(self.active_workers)
                for _ in range(free_procs):
                    if self.in_queue.empty():
                        continue
                    stream_resource = self.in_queue.get()
                    if stream_resource == "END":
                        self.close()
                        msg = {'type': MessageType.CHILD_ENDED.value}
                        self.out_queue.put(json.dumps(msg))
                        sys.exit()
                    self.invoke_stream_resource_worker(stream_resource)
            if not self.worker_result_queue.empty():
                while not self.worker_result_queue.empty():
                    msg = self.worker_result_queue.get()
                    self.active_workers.pop(msg['data']['resource_id'])
                    self.out_queue.put(json.dumps(msg))
            time.sleep(CONFIG_STREAM_IN_WAIT_TIME)

    def start_service(self):
        self.proc.start()

    def wait_to_end(self):
        self.proc.join()

    def close(self):
        self.active_workers.clear()
