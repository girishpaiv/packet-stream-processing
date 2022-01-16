class StreamResource:
    def __init__(self, resource_id):
        self.resource_id = resource_id
        self.packets_buffer = []

    def _insert_in_sorted_buffer(self, packet):
        """
        Insert packet based on it's index in the sorted buffer
        """
        i = 0
        while packet.index > self.packets_buffer[i].index:
            i += 1
        self.packets_buffer = self.packets_buffer[:i] + [packet] + self.packets_buffer[i:]

    def insert_packet(self, packet):
        if (not self.packets_buffer) or packet.index > self.packets_buffer[-1].index:
            self.packets_buffer.append(packet)
            return
        self._insert_in_sorted_buffer(packet)

    def is_ready_to_process(self):
        """
        Stream is ready to process if all the packets are received in the packets_buffer
        """
        last_pkt = self.packets_buffer[-1]
        if last_pkt.last_chunk_flag and len(self.packets_buffer) == last_pkt.index:
            return True
        return False
