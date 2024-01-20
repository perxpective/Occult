from scapy.all import rdpcap
import os
import csv
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import utils
import subprocess
import csv
import pandas as pd

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
                'packet_length': len(packet),
                'packet_summary': packet.summary()
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

# Extracting the Protcol Name and the Info field from the PCAP  using Tshark
def extract_pcap_info(input_pcap, output_csv):
    # Run tshark command to extract protocol name and info field
    tshark_command = [r"C:\Program Files\Wireshark\tshark.exe", "-r", input_pcap, "-T", "fields", "-e", "frame.number","-e", "_ws.col.Protocol", "-e", "_ws.col.Info"]

    try:
        result = subprocess.run(tshark_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        output_lines = result.stdout.splitlines()

        # Extract protocol name and info field
        # data = [(line.split('\t')[0], line.split('\t')[1]) for line in output_lines]
        data = [(line.split('\t')[0], line.split('\t')[1], line.split('\t')[2]) for line in output_lines]

        # Write to CSV
        with open(output_csv, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['frame_number','protocol_name', 'packet_information'])
            csv_writer.writerows(data)

        print(f"Extraction completed. Data saved to {output_csv}")

    except subprocess.CalledProcessError as e:
        print(f"Error running tshark command: {e}")
        print(f"stderr: {e.stderr}")


# Merging the outout (CSV) from both the scapy and Tshark into a single CSV File
def merge_csv_files(file1, file2, common_column, output_file):
    # Read CSV files into DataFrames
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Merge DataFrames based on the common column
    merged_df = pd.merge(df1, df2, on=common_column)

    # Write the merged DataFrame to a new CSV file
    merged_df.to_csv(output_file, index=False)
    os.remove(file2)
    print(f"File '{file2}' deleted successfully.")

    print(f"Merged data saved to {output_file}")



# This function, split_csv, takes a CSV file path as input.
def split_csv(csv_file):
    # Create an instance of the CSVLoader class, passing the CSV file path.
    csvLoader = CSVLoader(csv_file)

    # Use the load method of the CSVLoader instance to load the CSV file and obtain a list of CSV documents.
    csvdocs = csvLoader.load()

    # Apply a filtering operation to remove complex metadata from the loaded CSV documents using a utility function.
    csvdocs = utils.filter_complex_metadata(csvdocs)

    # Return the filtered CSV documents.
    return csvdocs

