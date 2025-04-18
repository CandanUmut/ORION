import numpy as np
import time
import RPi.GPIO as GPIO
from scipy.signal import find_peaks
import spidev
import matplotlib.pyplot as plt
from collections import deque
import threading

# ----------------------------
# CONFIGURATION
# ----------------------------
OUTPUT_PIN = 18          # GPIO pin to trigger output (MOSFET/Tesla/Piezo)
ADC_CHANNEL = 0          # MCP3008 channel for piezo sensor
SAMPLE_RATE = 1000       # Hz
BUFFER_SIZE = 500        # Number of samples in analysis buffer
AMPLITUDE_THRESHOLD = 700  # Minimum amplitude for resonance detection
BASE_PULSE_WIDTH = 0.01  # Base duration of output pulse (modulated later)

TARGET_FREQ = 38         # Target resonance frequency (Hz)
FREQ_TOLERANCE = 2       # Acceptable deviation for resonance window (Hz)

# ----------------------------
# HARDWARE SETUP
# ----------------------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(OUTPUT_PIN, GPIO.OUT)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

# ----------------------------
# FUNCTION: READ ADC
# ----------------------------
def read_adc(channel=ADC_CHANNEL):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# ----------------------------
# FUNCTION: OUTPUT PULSE
# ----------------------------
def trigger_pulse(adaptive_width):
    GPIO.output(OUTPUT_PIN, GPIO.HIGH)
    time.sleep(adaptive_width)
    GPIO.output(OUTPUT_PIN, GPIO.LOW)

# ----------------------------
# LIVE PLOT (Optional)
# ----------------------------
def live_plot(signal_deque):
    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot(np.arange(BUFFER_SIZE), np.zeros(BUFFER_SIZE))
    ax.set_ylim(0, 1024)
    ax.set_title("Real-Time Piezo Signal")
    ax.set_xlabel("Sample")
    ax.set_ylabel("Amplitude")

    while True:
        if len(signal_deque) == BUFFER_SIZE:
            line.set_ydata(signal_deque)
            fig.canvas.draw()
            fig.canvas.flush_events()
        time.sleep(0.05)

# ----------------------------
# MAIN LOOP
# ----------------------------
def main():
    print("ORION Adaptive Resonance Engine Started")
    signal_deque = deque([0]*BUFFER_SIZE, maxlen=BUFFER_SIZE)

    # Start live plotting in separate thread
    plot_thread = threading.Thread(target=live_plot, args=(signal_deque,), daemon=True)
    plot_thread.start()

    try:
        while True:
            val = read_adc()
            signal_deque.append(val)

            if len(signal_deque) == BUFFER_SIZE:
                signal_array = np.array(signal_deque)
                peaks, _ = find_peaks(signal_array, height=AMPLITUDE_THRESHOLD, distance=20)

                if len(peaks) > 1:
                    intervals = np.diff(peaks) / SAMPLE_RATE
                    avg_freq = 1.0 / np.mean(intervals)
                    print(f"[Freq: {avg_freq:.2f} Hz]")

                    in_band = abs(avg_freq - TARGET_FREQ) < FREQ_TOLERANCE
                    last_peak = peaks[-1]
                    is_peak = signal_array[last_peak] > AMPLITUDE_THRESHOLD

                    if in_band and is_peak:
                        # Adaptive pulse width based on frequency
                        adaptive_width = np.clip(avg_freq / 1000, 0.005, 0.05)
                        print(f">> Resonance LOCKED @ {avg_freq:.2f} Hz â Pulse Width: {adaptive_width:.3f}s")
                        trigger_pulse(adaptive_width)

            time.sleep(1.0 / SAMPLE_RATE)

    except KeyboardInterrupt:
        print("ORION Shutdown Initiated")
        GPIO.cleanup()
        spi.close()

if __name__ == "__main__":
    main()
