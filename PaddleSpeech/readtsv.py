import os
import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ThreadPoolExecutor

def cer(ref, hyp):
    n = len(ref)
    m = len(hyp)
    # Matrix of (n+1) x (m+1)
    d = np.zeros((n+1)*(m+1), dtype=np.uint8).reshape((n+1, m+1))
    
    # set endpoints
    for i in range(n+1):
        d[i][0] = i
    for j in range(m+1):
        d[0][j] = j
    
    # Fill in
    for i in range(1, n+1):
        for j in range(1, m+1):
            if ref[i-1] == hyp[j-1]:
                cost = 0
            else:
                cost = 1
            d[i][j] = min(d[i-1][j] + 1,      # delete
                          d[i][j-1] + 1,      # insert
                          d[i-1][j-1] + cost) # replace
    
    # Final result
    ANS = 0.0
    if float(n)!=0:
        ANS = d[n][m] / float(n)
    else:
        ANS = d[n][m]
    return ANS

def extract_data(file_path):
    data_map = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split('\t')
            if len(parts) > 3:
                mp3_file = parts[1]
                text = parts[3]
                data_map[mp3_file] = text
    return data_map

# Folder path
tra_folder_path = 'data_set_output_t'
#tra_folder_path = 'test_output_t'

check_file_path = 'Dataset\cv-corpus-17.0-2024-03-15\zh-TW\\validated.tsv'
#check_file_path = 'Dataset\cv-corpus-17.0-2024-03-15\zh-TW\invalidated.tsv'

filenames = [f for f in os.listdir(tra_folder_path) if f.endswith('.txt')]

# Extract from the dataset
result = extract_data(check_file_path)
# Store output
cer_by_length = {}

def process_file(file_name):
    input_file_path = os.path.join(tra_folder_path, file_name)
    with open(input_file_path, 'r', encoding='utf-8') as file:
        text = file.read() # Our output data
    
    new_name = file_name.rsplit('.', 1)[0] + ".mp3"
    if new_name in result:
        # Calculate
        cer_score = cer(text, result[new_name])
        # Store the result by length
        text_length = len(result[new_name])
        if text_length not in cer_by_length:
            cer_by_length[text_length] = []
        cer_by_length[text_length].append(cer_score)
        # print(f"CER: {cer_score:.4f}")

# Multi-threading
with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
    # Commit
    futures = [executor.submit(process_file, filename) for filename in filenames]

    # Make Sure all process done
    for future in futures:
        future.result()

# Sort results
sorted_cer_by_length = sorted(cer_by_length.items(), key=lambda x: x[0])

lengths = []
scores = []
tot_scores = 0.0
tot_len = 0
cnt = 0
for length, cer_list in sorted_cer_by_length:
    cnt = cnt + len(cer_list)
    avg_cer = sum(cer_list) / len(cer_list)
    if avg_cer < 1:
        lengths.append(length)
        #print(length)
        #print(avg_cer)
        scores.append(1-avg_cer)
        tot_len = tot_len + length
        tot_scores = tot_scores + (1-avg_cer)*length

print(f"Number of data: {(cnt):.4f}")
print(f"Total correct rate by CER: {(tot_scores / tot_len):.4f}")

plt.plot(lengths, scores, marker='o', linestyle='-')
plt.xlabel('Data length')
plt.ylabel('Correct Rate')
plt.title('Different Length & Correct Rate')
plt.ylim(0, 1)
plt.yticks([i/20 for i in range(20)])
plt.grid(True)
plt.show()
