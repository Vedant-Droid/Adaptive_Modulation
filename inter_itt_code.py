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
    'BPSK': {'M': 2, 'k': 1}, # k = log2(M)
    'QPSK': {'M': 4, 'k': 2},
    '16-QAM': {'M': 16, 'k': 4}
}

# ==================================================================
# --- PART A: BER Simulation Functions ---
# ==================================================================

def generate_bits(n):
    """Generates 'n' random bits (0s and 1s)."""
    return np.random.randint(0, 2, n)

def map_bits_to_symbols(bits, mod_name):
    """
    Maps a bit stream to complex constellation symbols.
    You need to implement the mapping logic for BPSK, QPSK, and 16-QAM.
    Ensure you normalize symbol power to an average of 1.
    """
    k = MODULATIONS[mod_name]['k']
    # 1. Reshape bits into groups of k
    # 2. Map each group to a complex symbol (e.g., QPSK: 00 -> (-1-1j)/sqrt(2))
    # 3. Return the array of complex symbols
    
    # --- YOUR MAPPING LOGIC HERE ---
    
    # Placeholder:
    num_symbols = len(bits) // k
    symbols = np.zeros(num_symbols, dtype=complex)
    return symbols

def add_awgn(symbols, snr_db):
    """
    Adds Additive White Gaussian Noise (AWGN) to symbols.
    The amount of noise depends on the SNR.
    """
    # 1. Convert SNR (dB) to linear scale: snr_linear = 10**(snr_db / 10)
    # 2. Signal power is 1 (due to normalization in mapping)
    # 3. Noise variance = 1 / snr_linear
    # 4. Generate complex noise:
    #    noise = np.sqrt(noise_variance / 2) * (np.random.randn(len(symbols)) + 1j * np.random.randn(len(symbols)))
    # 5. Return symbols + noise
    
    # --- YOUR NOISE LOGIC HERE ---
    
    # Placeholder:
    return symbols

def demapp_symbols_to_bits(noisy_symbols, mod_name):
    """
    Demaps noisy symbols back to bits using minimum distance (hard decision).
    """
    # 1. For each noisy symbol, find the *closest* ideal constellation point.
    # 2. Map that ideal point back to its corresponding 'k' bits.
    # 3. Return the stream of demodulated bits.
    
    # --- YOUR DEMAPPING LOGIC HERE ---
    
    # Placeholder:
    k = MODULATIONS[mod_name]['k']
    num_bits = len(noisy_symbols) * k
    bits_out = np.zeros(num_bits, dtype=int)
    return bits_out

def calculate_ber(bits_in, bits_out):
    """Counts errors and calculates the Bit Error Rate (BER)."""
    errors = np.sum(bits_in != bits_out)
    return errors / len(bits_in)

def run_ber_simulation():
    """Main loop for Part A."""
    print("Running Part A: BER Simulation...")
    ber_results = {mod: [] for mod in MODULATIONS}

    for mod_name in MODULATIONS:
        k = MODULATIONS[mod_name]['k']
        # Ensure number of bits is a multiple of k
        bits_to_send = (NUM_BITS // k) * k
        
        for snr_db in SNR_DB_RANGE:
            # 1. Generate bits
            tx_bits = generate_bits(bits_to_send)
            
            # 2. Map to symbols
            tx_symbols = map_bits_to_symbols(tx_bits, mod_name)
            
            # 3. Add noise
            rx_symbols = add_awgn(tx_symbols, snr_db)
            
            # 4. Demap to bits
            rx_bits = demapp_symbols_to_bits(rx_symbols, mod_name)
            
            # 5. Count errors
            ber = calculate_ber(tx_bits, rx_bits)
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
    plt.ylim(1e-7, 1.0) # Adjust as needed
    plt.savefig('ber_vs_snr.png')
    print("Saved ber_vs_snr.png")
    return ber_results

# ==================================================================
# --- PART B: Adaptive Modulation Controller ---
# ==================================================================

def get_time_varying_snr(num_intervals=1000):
    """Creates a time-varying SNR profile."""
    time = np.arange(num_intervals)
    # Example: A sine wave varying between 0 and 25 dB
    snr_t = 12.5 + 12.5 * np.sin(2 * np.pi * time / (num_intervals / 2))
    return time, snr_t

def adaptive_controller(snr):
    """
    Selects modulation based on SNR and predefined thresholds.
    *** YOU MUST CHOOSE THESE THRESHOLDS ***
    """
    # 1. Choose thresholds based on your ber_vs_snr.png plot
    #    (e.g., where BER drops below 1e-3 or 1e-5)
    THRESH_BPSK_TO_QPSK = 8   # EXAMPLE VALUE - CHANGE THIS
    THRESH_QPSK_TO_16QAM = 15 # EXAMPLE VALUE - CHANGE THIS
    
    if snr < THRESH_BPSK_TO_QPSK:
        return 'BPSK'
    elif snr < THRESH_QPSK_TO_16QAM:
        return 'QPSK'
    else:
        return '16-QAM'

def run_controller_simulation(time, snr_t):
    """Main logic for Part B."""
    print("Running Part B: Controller Simulation...")
    selected_mode_t = [adaptive_controller(snr) for snr in snr_t]
    
    # Plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))
    
    # Plot (a) SNR vs time
    ax1.plot(time, snr_t, label='SNR(t)')
    ax1.set_ylabel('SNR (dB)')
    ax1.set_title('Time-Varying Channel and Mode Selection')
    ax1.grid(True)
    ax1.legend()
    # Save individual plot
    fig_snr, ax_snr = plt.subplots()
    ax_snr.plot(time, snr_t)
    fig_snr.savefig('snr_vs_time.png')
    plt.close(fig_snr)
    
    # Plot (b) Selected mode vs time
    # Convert modes to numeric values for plotting
    mode_map = {'BPSK': 1, 'QPSK': 2, '16-QAM': 3}
    numeric_mode_t = [mode_map[mode] for mode in selected_mode_t]
    
    ax2.plot(time, numeric_mode_t, 'r.', label='Selected Mode')
    ax2.set_xlabel('Time (Symbol Intervals)')
    ax2.set_ylabel('Modulation Mode')
    ax2.set_yticks([1, 2, 3])
    ax2.set_yticklabels(['BPSK', 'QPSK', '16-QAM'])
    ax2.grid(True)
    ax2.legend()
    
    # Save individual plot
    fig_mode, ax_mode = plt.subplots()
    ax_mode.plot(time, numeric_mode_t, 'r.')
    ax_mode.set_yticks([1, 2, 3])
    ax_mode.set_yticklabels(['BPSK', 'QPSK', '16-QAM'])
    fig_mode.savefig('mode_vs_time.png')
    plt.close(fig_mode)

    print("Saved snr_vs_time.png and mode_vs_time.png")
    return selected_mode_t

# ==================================================================
# --- PART C: Performance Evaluation ---
# ==================================================================

def calculate_throughput(mod_name, ber):
    """Calculates effective throughput using the given formula."""
    k = MODULATIONS[mod_name]['k']
    # Throughput = R_nominal * log2(M) * (1 - BER)
    throughput = R_NOMINAL * k * (1.0 - ber)
    return throughput

def run_time_series_simulation(snr_t, selected_mode_t, BITS_PER_INTERVAL=1000):
    """Runs the full adaptive simulation over time."""
    print("Running Part C: Time-Series Performance Evaluation...")
    instantaneous_ber_t = []
    instantaneous_throughput_t = []
    
    total_bits_tx = 0
    total_bits_err = 0
    
    for i in range(len(snr_t)):
        current_snr = snr_t[i]
        current_mode = selected_mode_t[i]
        k = MODULATIONS[current_mode]['k']
        
        # Ensure bits_per_interval is multiple of k
        bits_to_send_interval = (BITS_PER_INTERVAL // k) * k
        if bits_to_send_interval == 0: bits_to_send_interval = k
        
        # 1. Run the sim chain for this *single* interval
        tx_bits = generate_bits(bits_to_send_interval)
        tx_symbols = map_bits_to_symbols(tx_bits, current_mode)
        rx_symbols = add_awgn(tx_symbols, current_snr)
        rx_bits = demapp_symbols_to_bits(rx_symbols, current_mode)
        
        # 2. Calculate instantaneous BER
        errors = np.sum(tx_bits != rx_bits)
        ber = errors / bits_to_send_interval
        instantaneous_ber_t.append(ber)
        
        # 3. Calculate instantaneous throughput
        throughput = calculate_throughput(current_mode, ber)
        instantaneous_throughput_t.append(throughput)
        
        # 4. Track totals for average
        total_bits_tx += bits_to_send_interval
        total_bits_err += errors

    # --- Calculate Averages ---
    avg_ber_adaptive = total_bits_err / total_bits_tx
    avg_throughput_adaptive = np.mean(instantaneous_throughput_t)
    
    print(f"Adaptive Scheme: Avg BER = {avg_ber_adaptive:.2e}, Avg Throughput = {avg_throughput_adaptive/1e6:.2f} Mbps")
    
    # --- Plot BER vs Time ---
    plt.figure()
    plt.plot(time, instantaneous_ber_t)
    plt.title('Instantaneous BER vs. Time (Adaptive)')
    plt.xlabel('Time (Symbol Intervals)')
    plt.ylabel('Instantaneous BER')
    plt.yscale('log')
    plt.grid(True, which='both')
    plt.savefig('ber_vs_time.png')
    print("Saved ber_vs_time.png")
    
    # --- Data for Summary Table ---
    # YOU NEED TO RE-RUN THE SIMULATION for fixed modes
    # This involves looping through snr_t 3 times (once for each fixed mode)
    # and calculating the average BER and throughput for each.
    
    # --- (IMPLEMENT FIXED SCHEME SIMULATIONS HERE) ---
    # avg_ber_fixed_bpsk, avg_tp_fixed_bpsk = ...
    # avg_ber_fixed_qpsk, avg_tp_fixed_qpsk = ...
    # avg_ber_fixed_16qam, avg_tp_fixed_16qam = ...
    
    summary_data = {
        'Scheme': ['Fixed BPSK', 'Fixed QPSK', 'Fixed 16-QAM', 'Adaptive'],
        'Average BER': [np.nan, np.nan, np.nan, avg_ber_adaptive],
        'Average Throughput (Mbps)': [np.nan, np.nan, np.nan, avg_throughput_adaptive / 1e6]
    }
    df = pd.DataFrame(summary_data)
    df.to_csv('summary_table.csv', index=False)
    print("Saved summary_table.csv (you must fill in 'nan' values)")
    
    # --- Throughput vs. SNR Plot ---
    # The prompt asks for "Throughput vs *average* SNR".
    # This is an advanced plot that requires running this *entire* Part C
    # simulation multiple times for different *average* SNRs.
    # A simpler, valid plot is "Instantaneous Throughput vs. Instantaneous SNR".
    
    plt.figure()
    plt.scatter(snr_t, instantaneous_throughput_t, alpha=0.3, label='Adaptive (Instantaneous)')
    plt.title('Instantaneous Throughput vs. Instantaneous SNR')
    plt.xlabel('SNR (dB)')
    plt.ylabel('Throughput (bps)')
    plt.grid(True)
    plt.legend()
    # This is a substitute for the requested 'throughput_vs_snr.png'
    plt.savefig('throughput_vs_snr_instantaneous.png')
    print("Saved 'throughput_vs_snr_instantaneous.png' as an example plot.")
    

# ==================================================================
# --- Main Execution ---
# ==================================================================
if __name__ == "__main__":
    # Part A
    ber_data = run_ber_simulation()
    
    # Part B
    time, snr_t = get_time_varying_snr()
    selected_mode_t = run_controller_simulation(time, snr_t)
    
    # Part C
    run_time_series_simulation(snr_t, selected_mode_t)
    
    print("\nSimulation complete. Check for generated .png and .csv files.")