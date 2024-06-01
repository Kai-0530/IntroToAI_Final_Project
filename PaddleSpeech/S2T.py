from opencc import OpenCC
import os
from concurrent.futures import ThreadPoolExecutor

# Folder path
sim_folder_path = 'data_set_output'
tra_folder_path = 'data_set_output_t'

# Get filenames
filenames = [f for f in os.listdir(sim_folder_path) if f.endswith('.txt')]

# Define Function
def convert_file(filename):
    try:
        input_file_path = os.path.join(sim_folder_path, filename)
        with open(input_file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        simplified_text = OpenCC('s2t').convert(text)

        output_file_path = os.path.join(tra_folder_path, filename)
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(simplified_text)

        print("Saved as", output_file_path)
    except Exception as e:
        print(f"File: {filename} error：{e}")

# Multi-Thread to boost
with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
    # Commit
    futures = [executor.submit(convert_file, filename) for filename in filenames]

    # Make Sure all process done
    for future in futures:
        future.result()

print("Complete!")
