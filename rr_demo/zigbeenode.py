"""ZigBeeNode - ZigBee node implementation.

This module does ZigBee stuff!
"""
from xbee import ZigBee
import serial


class ZigBeeNode(ZigBee):

    BAUD_RATE = 9600
    API_MODE_ESCAPED = True
    MAX_FRAME_ID = 255

    def __init__(self, serial_port, baud_rate=BAUD_RATE):

        self.serial = serial.Serial(serial_port, baud_rate)
        super(ZigBeeNode, self).__init__(
            self.serial, escaped=self.API_MODE_ESCAPED
        )

        self.tx_frame_id = 1

    def _at_cmd(self, command):

        self.at(command=command)
        response = self.wait_read_frame()
        return response

    def mac_addr(self):

        serial_low = self._at_cmd(command='SL').get('parameter', 0xFFFFFFFF)
        serial_high = self._at_cmd(command='SH').get('parameter', 0xFFFFFFFF)
        return '{}:{}'.format(
            self.addr_str(serial_high), self.addr_str(serial_low)
        )

    def is_coordinator(self):

        response = self._at_cmd(command='CE')
        return ord(response['parameter']) == 1

    def discover_network(self):

        response = self._at_cmd(command='ND')
        remote_addr = response['parameter']['source_addr_long']
        return [remote_addr]

    def addr_str(self, addr):
        return ':'.join('{:02x}'.format(ord(c)) for c in addr)

    def send_msg(self, *args, **kwargs):
        tx_args = {'data': args[0]}
        if 'addr' in kwargs:
            tx_args['dest_addr_long'] = kwargs['addr']

        tx_frame_status = kwargs.get('tx_frame_status', False)
        tx_args['frame_id'] = chr(self.tx_frame_id if tx_frame_status else 0)

        self.tx(**tx_args)

        if tx_frame_status:
            tx_status_response = self.wait_read_frame()
            tx_status_ok = (
                (tx_status_response.get('id') == 'tx_status') and
                (ord(tx_status_response.get('deliver_status')) == 0) and
                (ord(tx_status_response.get('frame_id')) == self.tx_frame_id)
            )

            self.tx_frame_id = self.tx_frame_id % self.MAX_FRAME_ID + 1
        else:
            tx_status_ok = True

        return tx_status_ok

    def recv_msg(self):

        frame = self.wait_read_frame()
        data = frame.get('rf_data')
        addr = frame.get('source_addr_long')
        return (data, addr)
