import time


class AncillaryService:
    @staticmethod
    def convert_payload_to_array(payload):
        """
        Process payload and return a list of word lengths
        :param payload: String with words separated by space. Eg. "a bbb cdds wqe f"
        :return: An array of integers representing the number of characters in each word in the input string.
        """
        # time.sleep(2)
        # return payload.split()
        return [len(word) for word in payload.split()]
