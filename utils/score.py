import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from Brachyphisis_Signal_Detectors.utils.filesystem.selectionfiles import SelectionFiles
from Brachyphisis_Signal_Detectors.utils.segment import Segments
from sklearn.metrics import balanced_accuracy_score

# To score the accuracy of the detectors

class SCORE:
    FALSE_NEG = 2
    TRUE_POS = 1
    TRUE_NEG = 0
    FALSE_POS = -1
    MANUAL_ANNOTATION = 2
    DETECTOR_ANNOTATION = -1
    

    def __init__(self, detector_selection:SelectionFiles, manual_selection:SelectionFiles,detector_name, seg_length=1) -> None:
        self.segment_length = seg_length
        self.detector_selection = detector_selection
        self.manual_selection = manual_selection
        self.detector_name = detector_name

        
    
    def calc_accuracy(self):
        # Number of Y / Number of Predictions
        total = self.score_count['True Positive'] + self.score_count['False Positive'] + self.score_count['False Negative'] + self.score_count['True Negative']
        accuracy = (self.score_count['True Positive'] + self.score_count['True Negative']) / total
        return accuracy
    def calc_precision(self):
        # TP / (TP + FP)
        total = self.score_count['True Positive'] + self.score_count['False Positive']
        precision = self.score_count['True Positive'] / total
        return precision
    def calc_recall(self):
        # TP / (TP + FN)
        total = self.score_count['True Positive'] + self.score_count['False Negative']
        recall = self.score_count['True Positive'] / total
        return recall
    def calc_f1_score(self):
        # (2 * Precision * Recall) / (Precision + Recall)
        precision = self.calc_precision()
        recall = self.calc_recall()
        f1score = (2 * precision * recall) / (precision + recall)
        return f1score

    def calc_sensitivity(self):
        # TP / (TP + FN)
        total = self.score_count['True Positive'] + self.score_count['False Negative']
        sensitivity = self.score_count['True Positive'] / total
        return sensitivity
    
    def calc_specificity(self):
        # TN / (TN + FP)
        total = self.score_count['True Negative'] + self.score_count['False Positive']
        specificity = self.score_count['True Negative'] / total
        return specificity
    
    def calc_balanced_accuracy(self):
        sensitivity = self.calc_sensitivity()
        specificity = self.calc_specificity()
        balanced_accuracy_score = (sensitivity + specificity) / 2
        return balanced_accuracy_score

    def confusion_matrix(self):
        self.score_count = self.scores['Label'].value_counts()
        print(self.score_count)
        try:
            tp = self.score_count['True Positive']
        except KeyError:
            print("No with True Positive")
            tp=0
        try:
            fp = self.score_count['False Positive']
        except KeyError:
            print("No False Positive")
            fp=0
        try:
            fn = self.score_count['False Negative']
        except KeyError:
            print("No with False Negative")
            fn=0
        try:
            tn = self.score_count['True Negative']
        except KeyError:
            print("No with True Negative")
            tn=0
        #total = tp + fp + fn + tn
        pos = tp + fn
        neg = tn + fp
        # create confusion matrix
        cm = [[tp/pos, fn/pos],
            [fp/neg, tn/neg]]
        
        
        # Convert to a DataFrame for better readability
        confusion_df = pd.DataFrame(cm, index=['Actual Positive', 'Actual Negative'],
                                    columns=['Predicted Positive', 'Predicted Negative'])

        print("Confusion Matrix:")
        print(confusion_df)

        font_size = 16  # Adjust factor as needed
        plt.rcParams.update({'font.size': font_size})  # Change 14 to the desired size

        # Visualize the confusion matrix using a heatmap
        plt.figure(figsize=(8, 6))
        sns.heatmap(confusion_df, annot=True, fmt='.3g', cmap='Blues',annot_kws={"size": font_size})
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.title(f'Confusion Matrix for {self.detector_name} model\n\nPrecision = {self.calc_precision():.4f}, Recall = {self.calc_recall():.4f}, F1-score = {self.calc_f1_score():.4f}\nBalanced Accuracy = {self.calc_balanced_accuracy():.4f}')
        plt.show()

    def scores_for_pr_curve(self, tag_name='Brachyphisis'):

        man_annotation = self.manual_selection.combine_selection_files()
        selections = self.detector_selection.combine_selection_files()

        man_annotation=man_annotation[man_annotation['View'] == 'Spectrogram 1']
        self.man_annotation=man_annotation[man_annotation['Tags'] == tag_name]
        self.selections=selections[selections['Tags'] == tag_name]
        
        self.segments = self.calc_values_for_segment_coverage()
        self.scores = self.label_detector_annotations_with_score()
        # calc score count for other methods
        self.score_count = self.scores['Label'].value_counts()

        return self.score_count

    def scores_for_model(self, write_file, tag_name='Brachyphisis'):

        man_annotation = self.manual_selection.combine_selection_files()
        selections = self.detector_selection.combine_selection_files()

        man_annotation=man_annotation[man_annotation['View'] == 'Spectrogram 1']
        self.man_annotation=man_annotation[man_annotation['Tags'] == tag_name]
        self.selections=selections[selections['Tags'] == tag_name]
        
        self.segments = self.calc_values_for_segment_coverage()
        self.scores = self.label_detector_annotations_with_score()
        self.scores.to_csv(f"{write_file}.txt",sep='\t')
        
        # calc score count for other methods
        self.score_count = self.scores['Label'].value_counts()

        return self.scores
    
    def calc_values_for_segment_coverage(self):
        """
        ## Params:
        man_annotation: pandas.Dataframe
            the manual annotations (true values)
        selections: pandas.Dataframe
            the selections made by detector. Needs to be for the same files as man_annotation
        segment_len: int
            length of segments in seconds
        """
        total_time = self.detector_selection.total_files * self.detector_selection.FILE_LENGTH
        self.segments = Segments(self.segment_length, total_time)

        man_index = 0 #index of man_annotations
        sel_index = 0 #index of selections
        for seg in self.segments.segments_list:
            man_row = self.man_annotation.iloc[man_index]
            sel_row = self.selections.iloc[sel_index]

            man_in_segment = seg.annotation_in_segment(man_row)
            
            while (man_in_segment):
                # while manual annotation is in this segment
                if seg.seg_score != self.MANUAL_ANNOTATION:
                    seg.seg_score = self.MANUAL_ANNOTATION
                
                seg.update_man_coverage(man_row)

                if (man_row["End Time (s)"] <= seg.end_time):
                    if man_index < len(self.man_annotation) - 1:
                        man_index += 1
                        man_row = self.man_annotation.iloc[man_index]
                        man_in_segment = seg.annotation_in_segment(man_row)
                    else:
                        man_in_segment = False
                else:
                    man_in_segment = False

            sel_in_segment = seg.annotation_in_segment(sel_row)
            while (sel_in_segment):
                # while detector annotation is in this segment
                if abs(seg.seg_score) != abs(self.DETECTOR_ANNOTATION):
                    seg.seg_score += self.DETECTOR_ANNOTATION
                
                seg.update_detector_coverage(sel_row)

                if (sel_row["End Time (s)"] <= seg.end_time):
                    if sel_index < len(self.selections) - 1:
                        sel_index += 1
                        sel_row = self.selections.iloc[sel_index]
                        sel_in_segment = seg.annotation_in_segment(sel_row)
                    else:
                        sel_in_segment = False
                else:
                    sel_in_segment = False   

        return self.segments

    def label_detector_annotations_with_score(self):
        value_map = {self.FALSE_NEG: 'False Negative', self.TRUE_POS: 'True Positive', self.TRUE_NEG: 'True Negative', self.FALSE_POS: 'False Positive'}
    
        df = pd.DataFrame({
            'Begin Time': [seg.start_time for seg in self.segments.segments_list],
            'End Time': [seg.end_time for seg in self.segments.segments_list],
            'Low Freq (Hz)': 17000,
            'High Freq (Hz)': 40000,
            'Tags': 'Brachyphisis',
            'Label': [value_map[seg.seg_score] for seg in self.segments.segments_list],
            'Manual Coverage of Segment (s)': [seg.manual_annot_coverage / seg.segment_length for seg in self.segments.segments_list],
            'Dectector Coverage of Segment (s)': [seg.detector_annot_coverage / seg.segment_length for seg in self.segments.segments_list],
        })

        return df
 
    def output_scores_to_file(self, filename):
        """
        Get a list of audio file paths.

        Parameters
        ----------
        filename : String
            The path to the file to output scores
            This file must have the headings: 
            - Site
            - Deployment
            - Number of files
            - Model Name
            - Segment Length
            - Accuracy
            - Precision
            - Recall
            - F1 Score

        Returns
        -------
        list
            The list of audio file paths.
        """
        precision = self.calc_precision()
        recall = self.calc_recall()
        accuracy = self.calc_accuracy()
        f1score = self.calc_f1_score()
        with open(filename, "a") as file:
            if not os.path.exists(filename):
                # write header
                file.write("Site,Deployment,Number of files,Model Name,Segment Length,Accuracy,Precision,Recall,F1 Score\n")
            # add scores
            file.write(f"{self.detector_selection.site},{self.detector_selection.dep},\
                       {self.detector_selection.total_files},{self.detector_name},{self.segment_length},\
                       {accuracy},{precision},{recall},{f1score}\n")
           
    def output_multiple_score_files(self,filename):
        tp = self.scores[self.scores['Label'] == 'True Positive']
        fp = self.scores[self.scores['Label'] == 'False Positive']
        fn = self.scores[self.scores['Label'] == 'False Negative']
        tn = self.scores[self.scores['Label'] == 'True Negative']

        write_file = f"{filename}_TP.txt"
        tp.to_csv(write_file,sep='\t')
        write_file = f"{filename}_FP.txt"
        fp.to_csv(write_file,sep='\t')
        write_file = f"{filename}_FN.txt"
        fn.to_csv(write_file,sep='\t')
        write_file = f"{filename}_TN.txt"
        tn.to_csv(write_file,sep='\t')

