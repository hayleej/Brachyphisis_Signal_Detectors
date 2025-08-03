import librosa
import scipy.signal as signal

def get_audio_segment(data, start_time, end_time, fs):
    start_sample = int(start_time * fs)
    end_sample = int(end_time * fs)

    audio_segment = data[start_sample:end_sample]
    return audio_segment

# High-pass filtering of over 8kHz with scipy.signal
def butter_highpass(cutoff_freq, fs, order=4):
    nyquist_rate = fs / 2
    normal_cutoff = cutoff_freq / nyquist_rate
    b, a = signal.butter(order, Wn=normal_cutoff, btype='high', analog=False)
    return b,a

def highpass_filter(data, cutoff_freq, fs, order=4):
    b, a = butter_highpass(cutoff_freq,fs,order)
    y = signal.filtfilt(b, a , data)
    return y


def get_filtered_audio_from_file(filename, filter_cutoff_freq):
    """
    Output:
        filtered_audio
        audio_data
        sample_rate
    """
    audio_data, sample_rate = librosa.load(filename,sr=None) # sr=None preserves original sampling rate
    #* parameters for filter
    order_filter = 4
    filtered_audio = highpass_filter(audio_data, filter_cutoff_freq, sample_rate,order_filter)
    return filtered_audio, audio_data, sample_rate


