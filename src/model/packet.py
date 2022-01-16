class Packet:
    def __init__(self, packet_json):
        self.resource_id = packet_json['resource_id']
        self.payload = packet_json['payload']
        self.index = packet_json['index']
        self.last_chunk_flag = packet_json['last_chunk_flag']
