import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# --- Constants and Specifications ---
SNR_DB_MIN = 0
SNR_DB_MAX = 25
SNR_DB_RANGE = np.arange(SNR_DB_MIN, SNR_DB_MAX + 1)
NUM_BITS = int(1e6)  # Number of bits for BER simulation
R_NOMINAL = 1e6      # 1 Mbps
MODULATIONS = {
    'BPSK': {'M': 2, 'k': 1, 'constellation': np.array([-1, 1])},
    'QPSK': {'M': 4, 'k': 2, 'constellation': np.array([-1-1j, -1+1j, 1-1j, 1+1j]) / np.sqrt(2)},
    '16-QAM': {'M': 16, 'k': 4, 'constellation': np.array([
        -3-3j, -3-1j, -3+1j, -3+3j,
        -1-3j, -1-1j, -1+1j, -1+3j,
         1-3j,  1-1j,  1+1j,  1+3j,
         3-3j,  3-1j,  3+1j,  3+3j
    ]) / np.sqrt(10)}
}
# Gray-coded bit mappings for demapping
BIT_MAP = {
    'BPSK': {0: [0], 1: [1]},
    'QPSK': {0: [0,0], 1: [0,1], 2: [1,0], 3: [1,1]},
    '16-QAM': {
        0: [0,0,0,0], 1: [0,0,0,1], 3: [0,0,1,0], 2: [0,0,1,1],
        4: [0,1,0,0], 5: [0,1,0,1], 7: [0,1,1,0], 6: [0,1,1,1],
        12: [1,0,0,0], 13: [1,0,0,1], 15: [1,0,1,0], 14: [1,0,1,1],
        8: [1,1,0,0], 9: [1,1,0,1], 11: [1,1,1,0], 10: [1,1,1,1]
    }
}


# ==================================================================
# --- PART A: BER Simulation Functions ---
# ==================================================================

def generate_bits(n):
    """Generates 'n' random bits (0s and 1s)."""
    return np.random.randint(0, 2, n)

def map_bits_to_symbols(bits, mod_name):
    """Maps a bit stream to complex constellation symbols."""
    k = MODULATIONS[mod_name]['k']
    constellation = MODULATIONS[mod_name]['constellation']
    
    # Reshape bits into groups of k and convert to integer indices
    bit_groups = bits.reshape(-1, k)
    # --- FIX: Padding was on the wrong side. Pad with zeros on the right. ---
    padded_bits = np.pad(bit_groups, ((0,0),(0, 8-k)), 'constant')
    indices = np.packbits(padded_bits, axis=1, bitorder='little').flatten()
    
    # Handle Gray code mapping for QPSK and 16-QAM
    if mod_name == 'QPSK':
        gray_map = {0:0, 1:1, 3:2, 2:3}
        indices = np.array([gray_map[i] for i in indices])
    elif mod_name == '16-QAM':
        gray_map = {
            0:0, 1:1, 3:2, 2:3,
            7:4, 6:5, 4:6, 5:7,
            15:8, 14:9, 12:10, 13:11,
            11:12, 10:13, 8:14, 9:15
        }
        indices = np.array([gray_map[i] for i in indices])

    return constellation[indices]

def add_awgn(symbols, snr_db):
    """Adds Additive White Gaussian Noise (AWGN) to symbols."""
    snr_linear = 10**(snr_db / 10.0)
    # Signal power is 1 due to normalization
    noise_power = 1.0 / snr_linear
    # Generate complex noise
    noise = np.sqrt(noise_power / 2.0) * (np.random.randn(len(symbols)) + 1j * np.random.randn(len(symbols)))
    return symbols + noise

def demapp_symbols_to_bits(noisy_symbols, mod_name):
    """Demaps noisy symbols back to bits using minimum distance."""
    constellation = MODULATIONS[mod_name]['constellation']
    bit_mapping = BIT_MAP[mod_name]
    
    demapped_bits = []
    for sym in noisy_symbols:
        # Find the index of the closest constellation point
        distances = np.abs(sym - constellation)
        closest_index = np.argmin(distances)
        demapped_bits.extend(bit_mapping[closest_index])
        
    return np.array(demapped_bits)

def calculate_ber(bits_in, bits_out):
    """Counts errors and calculates the Bit Error Rate (BER)."""
    if len(bits_in) != len(bits_out):
        return 1.0 # Return max error if lengths mismatch
    errors = np.sum(bits_in != bits_out)
    return errors / len(bits_in)

def run_ber_simulation():
    """Main loop for Part A."""
    print("Running Part A: BER Simulation...")
    ber_results = {mod: [] for mod in MODULATIONS}

    for mod_name in MODULATIONS:
        k = MODULATIONS[mod_name]['k']
        bits_to_send = (NUM_BITS // k) * k
        
        for snr_db in SNR_DB_RANGE:
            tx_bits = generate_bits(bits_to_send)
            tx_symbols = map_bits_to_symbols(tx_bits, mod_name)
            rx_symbols = add_awgn(tx_symbols, snr_db)
            rx_bits = demapp_symbols_to_bits(rx_symbols, mod_name)
            
            ber = calculate_ber(tx_bits, rx_bits)
            # To avoid BER of 0 which breaks log plots
            if ber == 0:
                ber = 1e-7
            ber_results[mod_name].append(ber)
            print(f"  {mod_name} @ {snr_db} dB, BER: {ber:.2e}")

    # Plotting
    plt.figure(figsize=(10, 6))
    for mod_name in MODULATIONS:
        plt.plot(SNR_DB_RANGE, ber_results[mod_name], 'o-', label=mod_name)
    
    plt.title('BER vs. SNR for BPSK, QPSK, and 16-QAM')
    plt.xlabel('SNR (dB)')
    plt.ylabel('Bit Error Rate (BER)')
    plt.yscale('log')
    plt.grid(True, which='both')
    plt.legend()
    plt.ylim(1e-7, 1.0)
    plt.savefig('ber_vs_snr.png')
    print("Saved ber_vs_snr.png")
    return ber_results

# ==================================================================
# --- PART B: Adaptive Modulation Controller ---
# ==================================================================

def get_time_varying_snr(num_intervals=1000):
    """Creates a time-varying SNR profile."""
    time = np.arange(num_intervals)
    snr_t = 12.5 + 12.5 * np.sin(2 * np.pi * time / (num_intervals / 2))
    return time, snr_t

def adaptive_controller(snr):
    """Selects modulation based on SNR and predefined thresholds."""
    # These thresholds are chosen based on the BER curves from Part A
    THRESH_BPSK_TO_QPSK = 7
    THRESH_QPSK_TO_16QAM = 14
    
    if snr < THRESH_BPSK_TO_QPSK:
        return 'BPSK'
    elif snr < THRESH_QPSK_TO_16QAM:
        return 'QPSK'
    else:
        return '16-QAM'

def run_controller_simulation(time, snr_t):
    """Main logic for Part B."""
    print("\nRunning Part B: Controller Simulation...")
    selected_mode_t = [adaptive_controller(snr) for snr in snr_t]
    
    # Plot SNR vs time
    plt.figure(figsize=(10, 4))
    plt.plot(time, snr_t, label='SNR(t)')
    plt.ylabel('SNR (dB)')
    plt.xlabel('Time (Symbol Intervals)')
    plt.title('Time-Varying SNR Profile')
    plt.grid(True)
    plt.savefig('snr_vs_time.png')
    plt.close()
    
    # Plot Selected mode vs time
    mode_map = {'BPSK': 1, 'QPSK': 2, '16-QAM': 3}
    numeric_mode_t = [mode_map[mode] for mode in selected_mode_t]
    plt.figure(figsize=(10, 4))
    plt.plot(time, numeric_mode_t, 'r.', label='Selected Mode')
    plt.xlabel('Time (Symbol Intervals)')
    plt.ylabel('Modulation Mode')
    plt.yticks([1, 2, 3], ['BPSK', 'QPSK', '16-QAM'])
    plt.grid(True)
    plt.title('Modulation Mode Selection Over Time')
    plt.savefig('mode_vs_time.png')
    plt.close()

    print("Saved snr_vs_time.png and mode_vs_time.png")
    return selected_mode_t

# ==================================================================
# --- PART C: Performance Evaluation ---
# ==================================================================

def calculate_throughput(mod_name, ber):
    """Calculates effective throughput using the given formula."""
    k = MODULATIONS[mod_name]['k']
    throughput = R_NOMINAL * k * (1.0 - ber)
    return throughput

def run_performance_simulation(snr_t, mode, BITS_PER_INTERVAL=1000):
    """Helper to run simulation for a given mode (fixed or adaptive)."""
    total_bits_tx = 0
    total_bits_err = 0
    instantaneous_throughput_t = []
    instantaneous_ber_t = []

    for i in range(len(snr_t)):
        current_snr = snr_t[i]
        current_mode = mode if isinstance(mode, str) else mode[i]
        k = MODULATIONS[current_mode]['k']
        
        bits_to_send_interval = (BITS_PER_INTERVAL // k) * k
        if bits_to_send_interval == 0: bits_to_send_interval = k
        
        tx_bits = generate_bits(bits_to_send_interval)
        tx_symbols = map_bits_to_symbols(tx_bits, current_mode)
        rx_symbols = add_awgn(tx_symbols, current_snr)
        rx_bits = demapp_symbols_to_bits(rx_symbols, current_mode)
        
        errors = np.sum(tx_bits != rx_bits)
        ber = errors / bits_to_send_interval
        instantaneous_ber_t.append(ber if ber > 0 else 1e-7)
        
        throughput = calculate_throughput(current_mode, ber)
        instantaneous_throughput_t.append(throughput)
        
        total_bits_tx += bits_to_send_interval
        total_bits_err += errors
    
    avg_ber = total_bits_err / total_bits_tx if total_bits_tx > 0 else 0
    avg_throughput = np.mean(instantaneous_throughput_t)
    return avg_ber, avg_throughput, instantaneous_ber_t, instantaneous_throughput_t


def run_final_evaluation(time, snr_t, selected_mode_t):
    """Runs all simulations for Part C and generates deliverables."""
    print("\nRunning Part C: Performance Evaluation...")

    # Run adaptive simulation
    avg_ber_ad, avg_tp_ad, ber_t_ad, tp_t_ad = run_performance_simulation(snr_t, selected_mode_t)
    print(f"  Adaptive: Avg BER = {avg_ber_ad:.2e}, Avg Throughput = {avg_tp_ad/1e6:.2f} Mbps")
    
    # Run fixed scheme simulations
    avg_ber_bpsk, avg_tp_bpsk, _, _ = run_performance_simulation(snr_t, 'BPSK')
    print(f"  Fixed BPSK: Avg BER = {avg_ber_bpsk:.2e}, Avg Throughput = {avg_tp_bpsk/1e6:.2f} Mbps")
    avg_ber_qpsk, avg_tp_qpsk, _, tp_t_qpsk = run_performance_simulation(snr_t, 'QPSK')
    print(f"  Fixed QPSK: Avg BER = {avg_ber_qpsk:.2e}, Avg Throughput = {avg_tp_qpsk/1e6:.2f} Mbps")
    avg_ber_16qam, avg_tp_16qam, _, _ = run_performance_simulation(snr_t, '16-QAM')
    print(f"  Fixed 16-QAM: Avg BER = {avg_ber_16qam:.2e}, Avg Throughput = {avg_tp_16qam/1e6:.2f} Mbps")
    
    # --- Create deliverables ---

    # BER vs Time plot
    plt.figure(figsize=(10, 6))
    plt.plot(time, ber_t_ad)
    plt.title('Instantaneous BER vs. Time (Adaptive Scheme)')
    plt.xlabel('Time (Symbol Intervals)')
    plt.ylabel('Instantaneous BER')
    plt.yscale('log')
    plt.grid(True, which='both')
    plt.savefig('ber_vs_time.png')
    plt.close()
    print("Saved ber_vs_time.png")
    
    # Throughput vs SNR plot
    plt.figure(figsize=(10, 6))
    plt.scatter(snr_t, tp_t_ad, alpha=0.3, label='Adaptive Scheme', s=10)
    plt.scatter(snr_t, tp_t_qpsk, alpha=0.3, label='Fixed QPSK Baseline', s=10, c='r')
    plt.title('Instantaneous Throughput vs. SNR')
    plt.xlabel('SNR (dB)')
    plt.ylabel('Throughput (bps)')
    plt.grid(True)
    plt.legend()
    plt.savefig('throughput_vs_snr.png')
    plt.close()
    print("Saved throughput_vs_snr.png")

    # Summary table
    summary_data = {
        'Scheme': ['Fixed BPSK', 'Fixed QPSK', 'Fixed 16-QAM', 'Adaptive'],
        'Average BER': [avg_ber_bpsk, avg_ber_qpsk, avg_ber_16qam, avg_ber_ad],
        'Average Throughput (Mbps)': [avg_tp_bpsk/1e6, avg_tp_qpsk/1e6, avg_tp_16qam/1e6, avg_tp_ad/1e6]
    }
    df = pd.DataFrame(summary_data)
    df.to_csv('summary_table.csv', index=False, float_format='%.6f')
    print("Saved summary_table.csv")
    
# ==================================================================
# --- Main Execution ---
# ==================================================================
if __name__ == "__main__":
    run_ber_simulation()
    time, snr_t = get_time_varying_snr()
    selected_mode_t = run_controller_simulation(time, snr_t)
    run_final_evaluation(time, snr_t, selected_mode_t)
    
    print("\nSimulation complete. All deliverables have been generated.")
