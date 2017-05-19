"""Demo ZigBee request/response transmitter script."""
from zigbeenode import ZigBeeNode

import sys
import json


DEFAULT_PORT = '/dev/ttyUSB0'
DEFAULT_BAUD_RATE = 57600

if __name__ == '__main__':

    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = DEFAULT_PORT

    zigbee = ZigBeeNode(port, DEFAULT_BAUD_RATE)

    print('Connected to ZB node on port {} with MAC address {}'.format(
        port, zigbee.mac_addr()
    ))
    print('This node is {}the network coordinator'.format(
        '' if zigbee.is_coordinator() else 'not '
    ))

    print('Discovering remote nodes in network ...')
    remote_nodes = zigbee.discover_network()

    print('Found {} remote nodes:'.format(len(remote_nodes)))
    for node in remote_nodes:
        print('    ', zigbee.addr_str(node))

    print(
        'Sending message sequence to remote node. Hit Ctrl-C to interrupt...'
    )

    seq_count = 0
    dest_node_addr = remote_nodes[0]
    while True:
        try:
            msg = json.dumps(
                {'type': 'request', 'seq': seq_count},
                separators=(',', ':')
            )
            zigbee.send_msg(msg, addr=dest_node_addr, tx_frame_status=True)

            (msg_data, msg_source) = zigbee.recv_msg()
            msg_source_str = zigbee.addr_str(msg_source)
            try:
                msg = json.loads(msg_data)
                if msg.get('type') == 'response':
                    seq = msg.get('seq', -1)
                    print(
                        'Got response message from node {} '
                        'with sequence ID {}'.format(msg_source_str, seq)
                    )
                else:
                    print(
                        'Got unrecognised JSON message from node {}: '
                        '{}'.format(msg_source_str, msg_data)
                    )
            except ValueError as e:
                print(
                    'Failed to decode JSON message from node: {}: '
                    '{} ({})'.format(msg_source, e, msg_data)
                )

            seq_count += 1
        except KeyboardInterrupt:
            break
