from sniffer import Sniffer
from dataclasses import asdict

def print_packet(packet_info):
    data = asdict(packet_info)
    print(f"[{data['timestamp']}] {data['protocol']} "
          f"{data['src_ip']}:{data['src_port']} → "
          f"{data['dst_ip']}:{data['dst_port']} | {data['summary']}")

if __name__ == '__main__':
    sniffer = Sniffer()
    sniffer.packet_callback = print_packet
    try:
        sniffer.start()
        while True:
            pass
    except KeyboardInterrupt:
        sniffer.stop()