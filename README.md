# packet-stream-processing
Services to handle data packets in a real-time stream

Overview:
This service does the following three jobs:
* Receive packets of data in real-time and pass this on to an ancillary service for
processing
* Collate the output from the ancillary service for a particular Primary Resource ID into a
single data packet
* Once all data packets for a particular Resource are received, pass on the collated output
data further for downstream processing with minimum latency by calling a webhook

Context and FAQs:
1. How do we receive the data?
We receive these data packets in a real-time stream. The time difference between the receipt of
two consecutive ordered data packets is random. Each data packet typically contains these four
things:
* Primary Resource ID (integer): This is the primary key for the data packet stream. We
would be receiving multiple data streams with different Primary Resource IDs
simultaneously (concurrently)
* Payload (bytes): This is some sort of binary data which will be passed on to the
ancillary service which gives us back an array of integers as the output
* Data Packet Index (integer): This is the desired ordering of the data. Some Primary
Resources would have only 1 chunk (packet), some may have multiple chunks of data.
We may receive the data packets slightly out of order (we qualify what slightly means in
the FAQs below) in the real-time stream. This quirk of a potential out-of-order delivery of
incoming packets should be handled well by this service
* Last Chunk Flag (boolean): This is a flag indicating if it is the last data chunk (packet)
for a particular Primary Resource ID
2. What does the ancillary service do?
* The ancillary service is an established service that takes the payload (series of bytes) as
the input and converts it into an array of integers
* This is a long-running job and it works in a synchronous manner. We will have to
make a waiting call and this will return the array
* This service treats each request independent of others and thus does NOT care about
the data packets to be ordered
3. Do we have a measure of out-of-order for the data packets?
We are getting the data packets in the real-time stream from a potentially distributed system,
hence can slightly be out of order.
We have some guarantee for the measure of out-of-order for these data packets. It is safe to
assume no packet will be out of order for more than 60 seconds. What this means is: If we
receive an out-of-order packet, we know that within 60 seconds, we will receive the missing data
packets.
5. Will the data packets be re-transmitted?
There is no provision for re-transmission; hence, we need to build a service that does not drop
any data packets and consumes them in real-time.
6. How do we send the data packets for downstream processing?
We need to get the data packets, i.e., the output from the ancillary service and collate them into
a single array (correctly ordered) for a particular Primary Resource ID and then pass it on to the
downstream service
Simplifying some assumptions:
Having laid out the problem as it appears in production scenarios, we now make some
simplifying assumptions. These are given below and are
expected to be used as one goes about implementing the code for the above problem
statement.
* The payload data is simulated by a simple string containing multiple words separated by
a space
* The “ancillary service” is a simple function that takes in a string consisting of several
space-separated words and returns an array of integers representing the length in
characters of each word in the input string. Thus, the output is a list whose length is the
same as the number of words in the input string. The order in which the integers are
presented in the output list is the same order in which the words appear in the input
string. Note that this simple construct allows us to maintain a characteristic that the
length (or size) of the output of the ancillary service is proportional to the length (or size)
of the input string
* The combined output across data packets of a single Primary Resource ID is the
concatenation of the output lists (in the correct ordering as given by data packet indices)
* We simulate the downstream webhook by writing this output data (as plain text, with one
integer of the list per line) to a file with the filename referencing the Primary Resource
ID

Miscellaneous Notes:
* There are (at least) two available design choices to get the packets in order and process
through the ancillary service: utilize the packets as and when we receive them, or use
them when we have all the data with us. We would love to see an explanation of what
you choose and why!
* Feel free to choose the language of your choice. An explanation for your choice would
be great, and might show how you look at the pros and cons of different programming
languages among the ones you are proficient in.
* In general, there are some intentionally ambiguous points in the above problem
statement. We encourage you to take a reasonable guess, state the assumption you are
making about the system and move on.
