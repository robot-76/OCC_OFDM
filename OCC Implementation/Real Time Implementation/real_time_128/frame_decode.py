
import numpy as np
from PIL import Image
import os
#from message_extraction import message_extract_code  # Import from the second .py file
import reedsolo

def binary_to_bytes(binary_str):
    return bytes(int(binary_str[i:i+8], 2) for i in range(0, len(binary_str), 8))

def bytes_to_binary(byte_data):
    return ''.join(format(byte, '08b') for byte in byte_data)

def bits_to_string(bits):
    """Convert a list of bits back to a string."""
    chars = [chr(int(''.join(map(str, bits[i:i + 8])), 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

def reverse_hermitian_symmetry_matrix(hermitian_symmetric_matrix):
    num_rows = hermitian_symmetric_matrix.shape[0]  
    qam_symbols_matrix = np.zeros((num_rows, 3), dtype=complex)                    
    for i in range(num_rows):
        qam_symbols_matrix[i, :] = hermitian_symmetric_matrix[i, 1:4]
    return qam_symbols_matrix

def qam4_to_binary(symbols):
    """Convert QAM-16 symbols back to a binary list, replace unmatched symbols with '1010'."""
    binary_list = []
    for RI in symbols:
        R = np.real(RI)
        I = np.imag(RI)

        if R >=0 and I>=0 :
            binary_list.append('00')
        elif R < 0 and I>=0 :
            binary_list.append('10')
        elif R < 0 and I < 0 :
            binary_list.append('11')
        elif R >=0 and I< 0 :
            binary_list.append('01')
    return binary_list

n = 15
k = 11
rs = reedsolo.RSCodec(n - k)

# Define a function for custom max value selection
def find_max_values(batch):
    length = len(batch)
    if length in [4, 5, 6]:  # Special case for lengths 4, 5, and 6
        # Find max value from the first 3 elements
        max_first_part = max(batch[:3])
        # Find max value from the remaining elements
        max_second_part = max(batch[3:]) if length > 3 else None
        return [max_first_part, max_second_part] if max_second_part is not None else [max_first_part]
    elif length in [7, 8, 9]:  # Special case for lengths 8 and 9
        # Max from the first 3 values
        max_first_part = max(batch[:3])
        # Max from the next 3 values
        max_second_part = max(batch[3:6])
        # Max from the remaining values
        max_remaining = max(batch[6:]) if length > 6 else None
        return [max_first_part, max_second_part, max_remaining] if max_remaining is not None else [max_first_part, max_second_part]
    elif length == 1:  # Special case for length 1
        return batch  # Return the single value as is
    elif length == 3:  # Special case for length 3
        return [max(batch)]  # Return the maximum of the batch
    else:  # Default case (no special rule)
        return [max(batch)]  # Return the overall max

def rx_data(value_p):
    s_batch = []
    rx_mess = []
    len_b = []
    start_idx = None
    for i, avg_pixel in enumerate(value_p):
        int_avg = int(avg_pixel)
        if int_avg == 0:
            if start_idx is not None and start_idx<i:
                b_in_b = value_p[start_idx:i]
                # call the max value function
                max1_values = find_max_values(b_in_b)
                rx_mess.append(max1_values)
                s_batch.append(b_in_b)
                len_b.append(len(b_in_b))
            start_idx = None
        else:
            if start_idx is None:
                start_idx = i

    if start_idx is not None and start_idx<len(value_p):
        bin_b = value_p[start_idx:]
        # call the max value function
        max2_values = find_max_values(bin_b)
        rx_mess.append(max2_values)
        s_batch.append(bin_b)
        len_b.append(len(bin_b))

    # print("batch value_p",s_batch)
    # print("each batch length",len_b)
    # print("rx message",rx_mess)

    # Flatten the list of max values batches and remove brackets/parentheses
    flat_max_values = [value for batch in rx_mess for value in batch]

    if len(flat_max_values)==128:
        # Convert to a space-separated string for cleaner output
        result = flat_max_values
        return result

def process_image(image_data): # directly data array is transfered fron another .py file
    batch_size = 128

    # Extract specific column range (e.g., columns 850 to 1000)
    columns_range_data = image_data[:, 750:1050]
    column_avg = np.mean(columns_range_data, axis=1)

    # Flatten the array of column-averaged values
    flat_column_avg = column_avg.flatten()
    batches_column_avg = []  # List to store batches

    l= len(flat_column_avg)
    start_idx = None

    i=0
    while i<l:
        if flat_column_avg[i]==0:
            zero_count =1
            while i+zero_count<l and flat_column_avg[i+zero_count]==0:
                zero_count+=1
            
            if zero_count>3:
                if start_idx is not None:
                    batches_column_avg.append(np.round(flat_column_avg[start_idx:i],5))
                    start_idx = None
                i+= zero_count-1
            else:
                if start_idx is None:
                    start_idx=i+zero_count
                i+=zero_count-1
        else:
            if start_idx is None:
                start_idx = i
        i+=1
    
    if start_idx is not None and start_idx<l:
        batches_column_avg.append(np.round(flat_column_avg[start_idx:],5))

    decoded_messages = []
    QAM_16 = []
    for i, batch in enumerate(batches_column_avg):
        output_rx = rx_data(batch)
        #print(f"Extracted max values (batch {i+1}): {output_rx}")

        if output_rx is not None:
                if len(output_rx) == batch_size:
                    rx_train = np.array(output_rx)
                    rx_reshaped = rx_train.reshape(-1, 128)
                    clipped_data = []
                    for batch in rx_reshaped:
                        lower_threshold = np.percentile(batch, 0)
                        upper_threshold = np.percentile(batch, 100)
                        batch_clipped = np.clip(batch, lower_threshold, upper_threshold)
                        clipped_data.append(batch_clipped)
                    clipped_data = np.array(clipped_data).reshape(-1) 
                    clip_rx_data = clipped_data.reshape(-1,128)
                    complex_ofdm = clip_rx_data + 0j
                    ofdm_symbols_reshaped = complex_ofdm.reshape(-1, 8) 
                    fft_ofdm_symbols = np.fft.fft(ofdm_symbols_reshaped, axis=1)

                    qam_symbols_matrix = reverse_hermitian_symmetry_matrix(fft_ofdm_symbols)
                    QAM_16 = np.concatenate(qam_symbols_matrix)
                    # import numpy as np
                    # import matplotlib.pyplot as plt
                    # plt.figure(figsize=(8, 8))
                    # plt.scatter(QAM_16.real, QAM_16.imag, color='blue', marker='o')
                    # plt.grid(True)
                    # plt.axhline(0, color='black',linewidth=0.5)
                    # plt.axvline(0, color='black',linewidth=0.5)
                    # plt.title("QAM Symbol Constellation")
                    # plt.xlabel("In-phase (Real)")
                    # plt.ylabel("Quadrature (Imaginary)")
                    # plt.show()

                    binary_output = qam4_to_binary(QAM_16)
                    binary_string = ''.join(binary_output)
                    try:
                        binary_bytes = binary_to_bytes(binary_string)
                        decoded_tuple = rs.decode(binary_bytes)
                        corrected_message = decoded_tuple[0]
                        decoded_binary = bytes_to_binary(corrected_message)
                    
                        corrected_bits = [int(bit) for bit in decoded_binary]
                        decoded_message = bits_to_string(corrected_bits)
                        if decoded_message:  # Only print if a message is successfully decoded
                            #print(f"Decoded message from : {decoded_message}")
                            decoded_messages.append(decoded_message)  # Append it to the list
                    except:
                        pass
                    

    return decoded_messages, QAM_16

            
