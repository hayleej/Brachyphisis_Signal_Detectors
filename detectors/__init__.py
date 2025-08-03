import abc
import numpy as np
from Brachyphisis_Signal_Detectors.utils.audio_processing import get_filtered_audio_from_file
from Brachyphisis_Signal_Detectors.utils.filesystem.audiofiles import AudioFiles
import pandas as pd

class BaseDetector(metaclass=abc.ABCMeta):
    def __init__(self, files:AudioFiles, filter_cutoff_freq=17000,max_interval_length=10000,min_disyllabic_len=5000) -> None:
        self.filter_cutoff_freq = filter_cutoff_freq
        self.files = files
        self.max_interval_len = max_interval_length
        self.min_disyllabic_len = min_disyllabic_len
        self.result = None
        self.all_selections = None
        self.filtered_audio = None

    def __str__(self) -> str:
        pass

    def get_filtered_audio(self, filename):
        filtered_audio, audio_data, self.sample_rate = get_filtered_audio_from_file(filename,self.filter_cutoff_freq)
        return filtered_audio
    
    def _get_segments_of_labels(self, ones=True):
        '''
        ones=True, means getting starts and ends of 1 segments
        ones=False, means getting starts and ends of 0 segments
        '''
        if ones:
            s_val = 2
            e_val = -2
            val = 2
        else:
            s_val = -2
            e_val = 2
            val = 0
        # Find the number of continuous 1s segments
        diffs = np.diff(self.result)
        starts = np.where(diffs == s_val)[0] + 1  # Start indices of 1s
        ends = np.where(diffs == e_val)[0] + 1   # End indices of 1s

        # If the array starts with 0, include the first segment
        if self.result[0] == val:
            starts = np.insert(starts, 0, 0)

        # If the array ends with 2, include the last segment
        if self.result[-1] == val:
            ends = np.append(ends, len(self.result) - 1)
        
        return starts, ends
    

    def replace_small_zero_sequences(self):
        if self.result is None:
            raise ValueError("self.result is None")
        # Find the number of continuous 0s segments
        starts, ends = self._get_segments_of_labels(ones=False)
        
        # Iterate over each sequence of zeros
        count = 0
        for start, end in zip(starts, ends):
            if (end - start) < self.max_interval_len:
                self.result[start:end] = 2
                count += 1
        return self.result

    def replace_small_ones_sequences(self):
        if self.result is None:
            raise ValueError("self.result is None")
        # Find the number of continuous 1s segments
        starts, ends = self._get_segments_of_labels(ones=True)
        
        count = 0
        # Iterate over each sequence of 1s
        for start, end in zip(starts, ends):
            if (end - start) < self.min_disyllabic_len:
                self.result[start:end] = 0
                count += 1
        return self.result
    

    def get_selections_for_single_file(self,filename):
        
        data = {
            "Begin Time (s)": [],
            "End Time (s)": [],
            "Low Freq (Hz)": [],
            "High Freq (Hz)": [],
            "Begin File": [],
            "File Offset (s)": [],
            "Tags": [],
            "Correct": []
        }
        df = pd.DataFrame(data)

        starts, ends = self._get_segments_of_labels(ones=True)

        for i in range(0, len(starts)):
            new_row = {
                "Begin Time (s)": starts[i] / self.sample_rate,
                "End Time (s)": ends[i] / self.sample_rate,
                "Low Freq (Hz)": 11000,
                "High Freq (Hz)": 37000,
                "Begin File": filename,
                "File Offset (s)": starts[i] / self.sample_rate,
                "Tags": "Brachyphisis",
                "Correct": "Y"
            }

            df.loc[i] = new_row

        return df


    def convert_single_file_to_deployment_selections(self,filename):
        df = self.get_selections_for_single_file(filename)
        
        # change begin and end time to be relative to the start of the deployment 
        # so it works for paging the whole deployment 
        df['Begin Time (s)'] = df['Begin Time (s)'] + (self.files.FILE_LENGTH * self.files.filenumber)
        df['End Time (s)'] = df['End Time (s)'] + (self.files.FILE_LENGTH * self.files.filenumber)

        return df

    def detect_with_detector(self,path_to_file, plot=False):
        raise NotImplementedError(
            'detect_with_detector method not implemented in derived class'
        )

    def detect_one_file(self, filename):
        try:
            path_to_file = f"{self.files.root_dir}/{filename}"
            print(f"Starting .... {filename}")
            self.detect_with_detector(path_to_file)
            selections = self.convert_single_file_to_deployment_selections(f"{filename}")
            self.all_selections = pd.concat([self.all_selections,selections], axis=0)
            self.files.update_filenumber()
        except FileNotFoundError:
            print(f"File ({filename}) does not exist ... Skipping......")


    def detect(self):
        # the max interval between disyllabic in number of samples 
        # the min length of disyllabic in number of samples
        data = {
            "Begin Time (s)": [],
            "End Time (s)": [],
            "Low Freq (Hz)": [],
            "High Freq (Hz)": [],
            "Begin File": [],
            "File Offset (s)": [],
            "Tags": [],
            "Correct": []
        }
        self.all_selections = pd.DataFrame(data)
        
        self.files.reset_filenumber()
        for filename in self.files.files_list:
            self.detect_one_file(filename)
        self.files.reset_filenumber()
        
        self.all_selections.to_csv(self.write_path, header=True, sep='\t')


__all__ = ['EnvelopeDetector', 'CorrelateDetector']