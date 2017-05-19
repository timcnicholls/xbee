"""Demo ZigBee request/response receiver script."""

from zigbeenode import ZigBeeNode
import json
import sys

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

    print(
        'Receiving message sequence from remote node. '
        'Hit Ctrl-C to interrupt...'
    )

    while True:
        try:
            response = {'type': 'error'}

            (data, source_addr) = zigbee.recv_msg()
            source_addr_str = zigbee.addr_str(source_addr)
            try:
                msg = json.loads(data)
                if msg.get('type') == 'request':
                    seq = msg.get('seq', -1)
                    print(
                        'Got request message from node {} '
                        'with sequence ID {}'.format(source_addr_str, seq)
                    )
                    response['type'] = 'response'
                    response['seq'] = seq
                else:
                    print(
                        'Got unrecognised JSON message from node {}: '
                        '{}'.format(source_addr_str, data)
                    )
            except ValueError as e:
                print(
                    'Failed to decode JSON message from node: {}: '
                    '{} ({})'.format(source_addr, e, data)
                )

            msg = json.dumps(response, separators=(',', ':'))
            zigbee.send_msg(msg, addr=source_addr, tx_frame_status=True)

        except KeyboardInterrupt:
            break
