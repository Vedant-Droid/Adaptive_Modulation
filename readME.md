# Adaptive Modulation for Reliable Wireless Links

This project implements and evaluates an adaptive modulation scheme (BPSK, QPSK, 16-QAM) over an AWGN channel. [cite_start]The goal is to design a controller that selects the optimal modulation order based on the instantaneous Signal-to-Noise Ratio (SNR) to maximize throughput while maintaining a low Bit Error Rate (BER)[cite: 2, 4].

This simulation is written in Python 3.

## Project Structure

The simulation is divided into three main parts as specified in the problem statement:

1.  [cite_start]**Part A: BER Simulation** [cite: 13]
    * [cite_start]Simulates the baseband transmission chain (bit generation, mapping, AWGN channel, demapping, error counting)[cite: 14, 15].
    * [cite_start]Generates and plots the BER vs. SNR curves for BPSK, QPSK, and 16-QAM[cite: 17, 18].

2.  [cite_start]**Part B: Adaptive Modulation Controller** [cite: 20]
    * [cite_start]Implements a time-varying SNR profile to simulate a changing channel[cite: 22].
    * [cite_start]A simple controller switches modulation based on predefined SNR thresholds (derived from Part A)[cite: 21, 23].
    * [cite_start]Plots the SNR vs. time and the corresponding selected modulation mode vs. time[cite: 24].

3.  [cite_start]**Part C: Performance Evaluation** [cite: 26]
    * [cite_start]Runs the full time-series simulation using the adaptive controller[cite: 27].
    * [cite_start]Computes and plots the instantaneous BER over time[cite: 28, 32].
    * [cite_start]Calculates and compares the average BER and effective throughput of the adaptive scheme against fixed modulation schemes (BPSK, QPSK, 16-QAM)[cite: 29, 30, 33, 34].

## Dependencies

The script requires the following Python libraries:
* [cite_start]**NumPy** [cite: 11, 55]
* [cite_start]**Matplotlib** [cite: 11, 55]
* **Pandas** (for `summary_table.csv`)

You can install them using pip:
```bash
pip install numpy matplotlib pandas