from . import BaseDetector
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate
from Brachyphisis_Signal_Detectors.utils.audio_processing import get_audio_segment

class CorrelateDetector(BaseDetector):
    def __init__(self,files, template_filename,template_start_time=0.062,template_end_time=0.144, filter_cutoff_freq=17000,max_interval_length=12000,min_disyllabic_len=5000,threshold=0.0125,write_path=None) -> None:
        
        super().__init__(files, filter_cutoff_freq,max_interval_length,min_disyllabic_len)
        if write_path is None:
            self.write_path = f"{self.files.root_dir}/Site{self.files.site}_Deployment{self.files.dep}_sel_{self.filter_cutoff_freq}Hz_{threshold}threshold_{self.max_interval_len}interval_{self.min_disyllabic_len}disyllabic.txt"
        else:
            self.write_path = write_path
        self.template, template_file_signal = self.get_template(template_filename,template_start_time,template_end_time)
        self.norm_factor = self.get_correlation_norm(template_file_signal)
        self.threshold = threshold

    def __str__(self) -> str:
        pass

    def get_template(self,template_filename,start_time,end_time):
        
        filtered_signal = self.get_filtered_audio(template_filename)

        filtered_template = get_audio_segment(filtered_signal, start_time, end_time, self.sample_rate)
        return filtered_template, filtered_signal
    
    def get_correlation_norm(self, template_file_signal):
        correlation = correlate(template_file_signal, self.template, mode='full')
        correlation = correlation[len(self.template)-1:]
        norm_factor = np.max(correlation)
        return norm_factor
    
    def normalisedCorrelate(self):
        # Calculate correlation
        correlation = correlate(self.filtered_audio, self.template, mode='full')
        correlation = correlation[len(self.template)-1:]
        cross_corr_normalised = correlation / self.norm_factor
        return cross_corr_normalised
        
    def correlateThreshold(self):
        binary_array = (abs(self.corr) > self.threshold).astype(int)
        binary_array = binary_array * 2
        return binary_array

    def detect_with_detector(self,filename, plot=False):
        # the max interval between disyllabic in number of samples 
        # the min length of disyllabic in number of samples
        
        self.filtered_audio = self.get_filtered_audio(filename)

        self.corr = self.normalisedCorrelate()

        self.result = self.correlateThreshold()    
        self.result = self.replace_small_zero_sequences()
        self.result = self.replace_small_ones_sequences()

        if plot:
            self.plot_threshold_result()
    
    def plot_threshold_result(self):
        # Plot the original audio, envelope, and binary array for visualization
        time = np.linspace(0, len(self.filtered_audio) / self.sample_rate, num=len(self.filtered_audio))
        plt.figure(figsize=(14, 6))

        plt.subplot(2, 1, 1)
        plt.plot(time, self.filtered_audio, label='Original Audio')
        plt.title('Original Signal')
        plt.plot(time, self.result * max(self.filtered_audio), label='Binary Array', color='green', alpha=0.6)
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')

        plt.subplot(2, 1, 2)
        plt.title('Correlation between Signal and Template')
        plt.plot(time, self.corr, label='Correlation', color='red')
        plt.plot(time, self.result * max(self.corr), label='Binary Array', color='green', alpha=0.6)
        plt.axhline(self.threshold,color='black',linestyle='--')
        plt.xlabel('Time (s)')
        plt.show()










