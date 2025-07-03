import numpy as np
import itertools
import reedsolo

import serial
import time


def manchester_encode(bits):
    encoded_bits = []
    for bit in bits:
        if bit == 1:
            encoded_bits.extend([0, 1])  # Manchester for 1: low-high
        else:
            encoded_bits.extend([1, 0])  # Manchester for 0: high-low
    return np.array(encoded_bits)

def string_to_bits(s):
    """ string to a list of bits."""
    return list(itertools.chain.from_iterable([list(map(int, f"{ord(c):08b}")) for c in s]))

def binary_to_bytes(binary_str):
    """ binary string to bytes."""
    byte_array = bytearray()
    for i in range(0, len(binary_str), 8):
        byte_array.append(int(binary_str[i:i+8], 2))
    return bytes(byte_array)

def bytes_to_binary(byte_array):
    """ bytes to a binary string."""
    return ''.join(f'{byte:08b}' for byte in byte_array)

def binary_to_qam16(bits):
    """binary list to QAM-16 symbols."""
    M = 4  # QAM-4
    bits_per_symbol = int(np.log2(M))  # 4 bits per QAM-16 symbol
    
    pad_length = (bits_per_symbol - len(bits) % bits_per_symbol) % bits_per_symbol
    padded_bits = np.append(bits, [0] * pad_length)
    
    mapping = {
        '00':  1+1j,  # Symbol 1
        '01':  1-1j,  # Symbol 2
        '11': -1-1j,  # Symbol 3
        '10': -1+1j   # Symbol 4
    }

    symbols = []
    for i in range(0, len(padded_bits), bits_per_symbol):
        bit_group = ''.join(str(int(bit)) for bit in padded_bits[i:i+bits_per_symbol])
        symbols.append(mapping[bit_group])

    return np.array(symbols)
import numpy as np

def hermitian_symmetry(symbols):
    N = 8 

    hermitian_symmetric = np.zeros(N, dtype=complex)  # Initialize the output array of size 8
    hermitian_symmetric[0] = 10 #DC value
    hermitian_symmetric[1] = symbols[0]            # QAM symbol 1
    hermitian_symmetric[2] = symbols[1]            # QAM symbol 2
    hermitian_symmetric[3] = symbols[2]            # QAM symbol 3
    hermitian_symmetric[4] = 0                     # Nyquist frequency (Subcarrier 5) set to zero

    hermitian_symmetric[5] = np.conj(symbols[2])   # Conjugate of QAM symbol 3
    hermitian_symmetric[6] = np.conj(symbols[1])    # Conjugate of QAM symbol 2
    hermitian_symmetric[7] = np.conj(symbols[0])   # Conjugate of QAM symbol 1

    return hermitian_symmetric


def create_ofdm_symbols(qam_symbols, num_subcarriers=8, symbols_per_ofdm=3):
    """OFDM symbols with Hermitian symmetry."""
    num_ofdm_symbols = len(qam_symbols) // symbols_per_ofdm  # Number of OFDM symbols
    ofdm_symbols = []  
    
    for i in range(num_ofdm_symbols):
        start_idx = i * symbols_per_ofdm
        end_idx = start_idx + symbols_per_ofdm
        qam_chunk = qam_symbols[start_idx:end_idx]
        hermitian_symmetric_seq = hermitian_symmetry(qam_chunk)
        time_domain_ofdm = np.fft.ifft(hermitian_symmetric_seq)
        ofdm_symbols.append(time_domain_ofdm)
    return np.array(ofdm_symbols)  

def clip_signal(x_t):
    alpha = 1.5
    sigma_x_t = np.std(x_t)
    b = alpha * sigma_x_t
    biased_signal = (x_t + b)*60 
    L = np.percentile(biased_signal, 0)
    U = np.percentile(biased_signal, 100)
    clipped_signal = np.clip(biased_signal, L, U)
    return clipped_signal
data="ID: 7 0001"
data_array = np.array(list(data))
bits = string_to_bits(data)
binary_str = ''.join(map(str, bits))
data_bytes = binary_to_bytes(binary_str)
n = 15
k = 11
rs = reedsolo.RSCodec(n - k)
encoded_data = rs.encode(data_bytes)
encoded_binary = bytes_to_binary(encoded_data)
binary_list = [int(bit) for bit in encoded_binary]
qam_symbols = binary_to_qam16(binary_list)
ofdm_symbols = create_ofdm_symbols(qam_symbols)

tx_signal_combined_real = np.concatenate([ofdm.real for ofdm in ofdm_symbols])

clipped_signal_example = clip_signal(tx_signal_combined_real)
clipped_signal_example = np.array([clipped_signal_example])
transmitted_signal = clipped_signal_example*1.2

normalized_signal = np.round(transmitted_signal).astype(int)
normalized_signal = normalized_signal.reshape(-1)
print(f"Normalized Signal Length: {len(normalized_signal)}")
formatted_list = ', '.join(map(str, normalized_signal))
print(f"{formatted_list}")

ser = serial.Serial('COM8', 9600, timeout=1)
time.sleep(2)  # Wait for Arduino to initialize

# Convert the formatted_list to a string and send it
ser.write((formatted_list + "\n").encode())

print("Data sent to Arduino.")
ser.close()
