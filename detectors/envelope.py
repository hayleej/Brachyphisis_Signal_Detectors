from . import BaseDetector
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter1d, maximum_filter1d

class EnvelopeDetector(BaseDetector):
    def __init__(self,files, filter_cutoff_freq=17000,max_interval_length=10000,min_disyllabic_len=5000,lower_faint=0.002,lower_loud=0.003, write_path=None) -> None:
        self.lower_faint = lower_faint
        self.lower_loud = lower_loud
        super().__init__(files, filter_cutoff_freq,max_interval_length,min_disyllabic_len)
        if write_path is None:
            self.write_path = f"{self.files.root_dir}/Site{self.files.site}_Deployment{self.files.dep}_sel_{self.filter_cutoff_freq}Hz_{self.lower_faint}lower{self.lower_loud}_{self.max_interval_len}interval_{self.min_disyllabic_len}disyllabic.txt"
        else:
            self.write_path = write_path

    def __str__(self) -> str:
        pass

    
    def calc_envelope_of_signal(self, max_window=500,uniform_window=500):
        analytic_signal = signal.hilbert(self.filtered_audio)
        amplitude_envelope = np.abs(analytic_signal)
        data = maximum_filter1d(amplitude_envelope, size=max_window)
        data = uniform_filter1d(data,size=uniform_window)
        return data

    def get_envelope_threshold(self, lower_threshold=0.003, upper_threshold=0.02):
        binary_array1 = (self.envelope_data > lower_threshold).astype(int)
        binary_array2 = (self.envelope_data < upper_threshold).astype(int)
        binary_array = binary_array1 + binary_array2
        # binarray1 + binarray2 = 2 when in range
        # binarray1 + binarray2 = 1 when spike
        # binarray1 + binarray2 = 0 when nothing
        for i in range(0,len(binary_array)):
            if binary_array[i] == 1:
                binary_array[i] = 0

        return binary_array

    def detect_with_detector(self, filename, plot=False):
        # the max interval between disyllabic in number of samples 
        # the min length of disyllabic in number of samples
        self.filtered_audio = self.get_filtered_audio(filename)
        self.envelope_data = self.calc_envelope_of_signal(500,500)
        
        if self.envelope_data.mean() < 0.0015:
            lower_threshold = self.lower_faint
            upper_threshold = 0.02
        else:
            lower_threshold = self.lower_loud
            upper_threshold = 0.02
        
        self.result = self.get_envelope_threshold(lower_threshold=lower_threshold, upper_threshold=upper_threshold)
        
        self.result = self.replace_small_zero_sequences()
        self.result = self.replace_small_ones_sequences()
        
        if plot:
            self.plot_threshold(lower_threshold, upper_threshold)

    def plot_threshold(self, lower_threshold, upper_threshold):
        # Plot the original audio, envelope, and binary array for visualization
        time = np.linspace(0, len(self.filtered_audio) / self.sample_rate, num=len(self.filtered_audio))
        plt.figure(figsize=(14, 6))
        plt.plot(time, self.filtered_audio, label='Original Audio')
        plt.plot(time, self.envelope_data, label='Envelope', color='red', linewidth=2, alpha=0.5)
        plt.plot(time, self.result * max(self.filtered_audio), label='Binary Array', color='green', alpha=0.6)
        plt.axhline(lower_threshold,color='black',linestyle='--')
        plt.axhline(upper_threshold,color='black',linestyle='--')
        plt.axhline(0,color='black',linestyle='--')
        plt.title('Envelope Detection with Binary Array')
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.show()

        
