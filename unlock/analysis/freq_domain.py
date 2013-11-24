import matplotlib.pyplot as plt
import numpy as np

# Input signal: 256 quadruples
input = []
for i in range(256):
    input.append([1232+i, 2323445+2*i, 34322+3*i, 232445+4*i])
signal = np.array(input)

# Get FFT for freq domain plot
sp = np.fft.fft(signal)
freq = np.fft.fftfreq(signal.shape[0])

# Plot signal in frequency domain
plt.figure(1)
plt.plot(freq, sp.real, freq, sp.imag)

# Plot spectrogram
plt.figure(2)
plt.specgram(signal, NFFT=1024)

plt.show()