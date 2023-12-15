from scapy.all import rdpcap
import os
import csv
from langchain.document_loaders.csv_loader import CSVLoader

# Extract important pcap fields to be added into a csv files
def extract_pcap_fields(pcap_file):
    packets = rdpcap(pcap_file)
    extracted_fields = []
    empty_field = 0  # Value to use for empty fields

    for i, packet in enumerate(packets, 1):
        try:
            print(packet)
            entry = {
                'frame_number': i,
                'src_mac': packet.src,
                'dst_mac': packet.dst,
                'eth_type': packet.type,
                'src_ip': packet['IP'].src if packet.haslayer('IP') else empty_field,
                'dst_ip': packet['IP'].dst if packet.haslayer('IP') else empty_field,
                'ip_proto': packet['IP'].proto if packet.haslayer('IP') else empty_field,
                'ip_ttl': packet['IP'].ttl if packet.haslayer('IP') else empty_field,
                'src_port': packet['TCP'].sport if packet.haslayer('TCP') else packet['UDP'].sport if packet.haslayer('UDP') else empty_field,
                'dst_port': packet['TCP'].dport if packet.haslayer('TCP') else packet['UDP'].dport if packet.haslayer('UDP') else empty_field,
                'tcp_flags': packet['TCP'].flags if packet.haslayer('TCP') else empty_field,
                'packet_time': packet.time,
                'packet_length': len(packet)
            }
            extracted_fields.append(entry)
        except AttributeError:
            raise("Error: Packet cannot be parsed!")
    return extracted_fields

# Writing all the extracted fields above to a csv file 
def write_to_csv(extracted_fields, csv_file):
    # Check if the CSV file exists, and create it if not
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='') as csvfile:
        fieldnames = extracted_fields[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # If the file doesn't exist, write the header row
        if not file_exists:
            writer.writeheader()

        # Write the data rows
        writer.writerows(extracted_fields)

def split_csv(csv_file):
    csvLoader = CSVLoader(csv_file)
    csvdocs = csvLoader.load()
    return csvdocs