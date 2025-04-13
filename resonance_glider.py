# Filename: pru_recursive_resonance_glide_simulation.py
"""
PRU Resonance Lab – Recursive Adaptive Resonance Glide Simulation
Author: Umut Candan
License: MIT License

Description:
This simulation models an energy-efficient, resonance-based propulsion system using
recursive adaptive frequency tuning. Inspired by the concept of Precomputed Relational Universe (PRU),
it visualizes the exponential movement of an object across a low-friction surface using micro-vibrations
instead of brute force.

The system:
- Emits a vibrational pulse at a tunable frequency
- Receives feedback (simulated) based on proximity to the system’s natural resonance
- Adjusts frequency over time toward optimal resonance
- Continuously emits resonant pulses to increase velocity and motion

This model proposes a new method of propulsion using harmonic amplification through recursive feedback loops.

Requirements:
- Python 3.x
- NumPy
- Matplotlib

Run with:
$ python pru_recursive_resonance_glide_simulation.py
"""

import numpy as np
import matplotlib.pyplot as plt

# Constants
mass = 0.1  # kg
amplitude = 0.0001  # vibration amplitude in meters (100 microns)
target_frequency = 980.0  # Hz, natural resonance of system
dt = 0.01  # time step (s)
max_steps = 2000  # total simulation steps
freq_step = 0.5  # frequency adjustment step size

# Pyramid resonance field multiplier
pyramid_focus_gain = 2.0  # amplification factor from focused geometry

# Feedback gain function (resonance response)
def resonance_feedback(frequency, target):
    delta = abs(frequency - target)
    return pyramid_focus_gain / (1 + 20 * delta**2)

# Initialize state variables
current_frequency = 300.0  # start from a low frequency
frequencies = []
resonance_gains = []
velocities = []
positions = []

velocity = 0.0
position = 0.0

# Simulation loop
for step in range(max_steps):
    gain = resonance_feedback(current_frequency, target_frequency)
    force = gain * amplitude * (2 * np.pi * current_frequency)**2
    acceleration = force / mass
    velocity += acceleration * dt
    position += velocity * dt

    # Log values
    frequencies.append(current_frequency)
    resonance_gains.append(gain)
    velocities.append(velocity)
    positions.append(position)

    # Adaptive recursive tuning
    if gain < 0.995:
        if current_frequency < target_frequency:
            current_frequency += freq_step
        else:
            current_frequency -= freq_step
    else:
        # Micro-tuning oscillation around optimal
        current_frequency += 0.1 * np.sin(step / 30.0)

# Plotting
fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

axs[0].plot(frequencies, label="Frequency (Hz)", color='blue')
axs[0].set_ylabel("Frequency (Hz)")
axs[0].legend()
axs[0].grid(True)

axs[1].plot(resonance_gains, label="Resonance Gain", color='orange')
axs[1].set_ylabel("Gain")
axs[1].legend()
axs[1].grid(True)

axs[2].plot(positions, label="Position (m)", color='green')
axs[2].set_ylabel("Position")
axs[2].set_xlabel("Time Step")
axs[2].legend()
axs[2].grid(True)

plt.suptitle("PRU Resonance Lab – Recursive Adaptive Resonance Glide Simulation")
plt.tight_layout()
plt.show()

# Print final state
print("Final Velocity (m/s):", velocity)
print("Final Position (m):", position)
