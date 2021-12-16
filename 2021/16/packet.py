# https://adventofcode.com/2021/day/16

from __future__ import annotations

import logging
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import reduce
from operator import mul
from timeit import default_timer as timer
from typing import Iterator

import pytest

INPUT_FILE = 'input.txt'
INPUT_TEST = 'input_test.txt'


@dataclass
class Message:
    """
    ID 0 sum packets - their value is the sum of the values of their sub-packets.
    ID 1 product packets - their value is the result of multiplying together the values of their sub-packets.
    ID 2 minimum packets - their value is the minimum of the values of their sub-packets.
    ID 3 maximum packets - their value is the maximum of the values of their sub-packets.
    ID 4 Literal Value - contains a single number
    ID 5 greater than packets - 1 if first sub-packet is greater than second sub-packet; otherwise 0
    ID 6 less than packets - 1 if first sub-packet is smaller than second sub-packet; otherwise 0
    ID 7 equal to packets - 1 if first sub-packet is equal to second sub-packet; otherwise 0
    """
    binary: str

    def __repr__(self) -> str:
        return self.binary

    def __len__(self) -> int:
        return len(self.binary)

    def read_bits(self, num_bits: int) -> str:
        result = self.binary[:num_bits]
        logging.debug(f'Reading {num_bits} bits from message of length {len(self)}.'
                      f' -> {result}')
        self.binary = self.binary[num_bits:]
        return result

    def read(self, num_bits: int) -> int:
        result = self.read_bits(num_bits)
        return int(result, 2)

    def parse(self) -> Packet:
        version = self.read(3)
        type_id = self.read(3)
        logging.debug(f'Parsing message ({len(self.binary)}):\n'
                      f'\t{self.binary}')

        if type_id == 4:
            packet = LiteralValuePacket(version=version, type_id=type_id, message=self)
        else:
            packet = OperatorPacket(version=version, type_id=type_id, message=self)
        return packet


@dataclass
class Packet(ABC):
    version: int
    type_id: int
    message: Message

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def parse(self) -> None:
        pass

    @abstractmethod
    def get_value(self) -> int:
        pass


@dataclass
class LiteralValuePacket(Packet):
    """
    - type_id = 4
    - padded to 4 bits
    - 1 b - next 4 bits contain value
        = 1 -> continue
        = 0 -> last part
    - e.g. 110.100.1-0111.1-1110.0-0101.000
        = ver 6, id 4, literal: 2021, padding
    """
    value: int = field(init=False)

    def __post_init__(self):
        self.parse()

    def __repr__(self) -> str:
        return repr(f'Version: {self.version}, Value: {self.value}')

    def get_value(self) -> int:
        return self.value

    def parse(self) -> None:
        logging.debug(f'Parsing LiteralValuePacket (ver: {self.version}) with message ({len(self.message)}):\n'
                      f'\t{self.message}')
        value = 0
        has_more_parts = 1
        while has_more_parts:
            has_more_parts = self.message.read(1)
            # value = (value * 16) + self.message.read(4)
            value = (value << 4) | self.message.read(4)
        self.value = value


@dataclass
class OperatorPacket(Packet):
    """
    - performs operation on sub-packets within
    - 1 bit - length type id
        -> 0 - 15 bits = total length of all sub-packets within
        -> 1 - 11 bits = number of sub-packets within
        -> sub-packet
    - e.g. 001.110.0-000000000011011 || 110.100-0-1010 | 010.100.1-0001.0-0100 || 0000000
    = ver 1, id 6, 0 len type id, total len = 27, literal sub-packet, literal sub-packet, padding
    """
    sub_packets: list[Packet] = field(default_factory=list, init=False)

    def __post_init__(self):
        self.parse()

    def __repr__(self) -> str:
        return repr(f'Version: {self.version}, Sub-packets: {len(self.sub_packets)}')

    def parse(self) -> None:
        logging.debug(f'Parsing OperatorPacket (ver: {self.version}) with message ({len(self.message)}):\n'
                      f'\t{self.message}')
        length_type_id = self.message.read(1)
        if length_type_id:
            packet_number = self.message.read(11)
            logging.debug(f'\tParsing {packet_number} sub-packets within length {len(self.message)}!\n'
                          f'\t\t -> {self.message}')
            while len(self.sub_packets) != packet_number:
                self.sub_packets.append(self.message.parse())

        else:
            packet_length = self.message.read(15)
            packet_bits = self.message.read_bits(packet_length)
            new_message = Message(packet_bits)
            logging.debug(f'\tParsing {packet_length} bits of sub-packets!\n'
                          f'\t\t -> {packet_bits}')
            while new_message.binary:
                self.sub_packets.append(new_message.parse())

    def get_value(self) -> int:
        if self.type_id == 0:
            return sum(packet.get_value() for packet in self.sub_packets)
        if self.type_id == 1:
            return reduce(mul, (packet.get_value() for packet in self.sub_packets))
        if self.type_id == 2:
            return min(packet.get_value() for packet in self.sub_packets)
        if self.type_id == 3:
            return max(packet.get_value() for packet in self.sub_packets)
        if self.type_id == 5:
            assert len(self.sub_packets) == 2
            return self.sub_packets[0].get_value() > self.sub_packets[1].get_value()
        if self.type_id == 6:
            assert len(self.sub_packets) == 2
            return self.sub_packets[0].get_value() < self.sub_packets[1].get_value()
        if self.type_id == 7:
            assert len(self.sub_packets) == 2
            return self.sub_packets[0].get_value() == self.sub_packets[1].get_value()
        raise ValueError(f'Unknown type ID: {self.type_id}')


def hex_to_binary(hex_str: str) -> str:
    data = bytes.fromhex(hex_str)
    return ''.join(f'{b:08b}' for b in data)


def parse_file(input_file: str) -> Message:
    """ Parse input file for hexadecimal string and convert it to Packet. """
    with open(input_file) as f:
        line = f.readline()

    binary_str = hex_to_binary(line)
    message = Message(binary_str)
    return message


def get_all_versions(packet: Packet) -> Iterator[int]:
    if isinstance(packet, LiteralValuePacket):
        yield packet.version
    elif isinstance(packet, OperatorPacket):
        yield packet.version
        for sub_packet in packet.sub_packets:
            yield from get_all_versions(sub_packet)


# part 1
def sum_versions(message: Message) -> int:
    """ Sum all versions parsed within packet and its sub-packets. """
    sum_version = 0
    packet = message.parse()
    for version in get_all_versions(packet):
        sum_version += version

    return sum_version


@pytest.mark.parametrize(
    "hex_str,expected", [
        ("8A004A801A8002F478", 16),
        ("620080001611562C8802118E34", 12),
        ("C0015000016115A2E0802F182340", 23),
        ("A0016C880162017C3686B18A3D4780", 31)
    ])
def test_parse_example(hex_str, expected):
    assert expected == sum_versions(Message(hex_to_binary(hex_str)))


# part 1
def calculate(message: Message) -> int:
    """ Calculate values parsed within packet and its sub-packets. """
    packet = message.parse()
    return packet.get_value()


@pytest.mark.parametrize(
    "hex_str,expected", [
        ("C200B40A82", 3),
        ("04005AC33890", 54),
        ("880086C3E88112", 7),
        ("CE00C43D881120", 9),
        ("D8005AC2A8F0", 1),
        ("F600BC2D8F", 0),
        ("9C005AC2F8F0", 0),
        ("9C0141080250320F1802104A08", 1)
    ])
def test_packet_calculation(hex_str, expected):
    test = calculate(Message(hex_to_binary(hex_str)))
    assert expected == test


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    start_time = timer()
    total_sum = sum_versions(parse_file(INPUT_FILE))
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Total sum of all packet versions is {total_sum}.')

    start_time = timer()
    total_result = calculate(parse_file(INPUT_FILE))
    end_time = timer()
    logging.info(f'({end_time - start_time:.4f}s elapsed) '
                 f'Total result of calculating all packets contained is {total_result}.')
