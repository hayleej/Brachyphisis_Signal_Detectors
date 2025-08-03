
from typing import List


class Segments:
    def __init__(self, segment_length, total_time) -> None:
        self.segment_length = segment_length
        self.number_of_segments = total_time // segment_length
        self.segments_list = self.create_segment_list()

    def create_segment_list(self):
        segment_list: List[Segment] = []
        for seg_num in range(self.number_of_segments):
            start = seg_num * self.segment_length
            end = start + self.segment_length
            segment_list.append(Segment(start,end,seg_num))
        return segment_list

class Segment:
    def __init__(self, start, end, seg_num) -> None:
        self.start_time = start
        self.end_time = end
        self.segment_length = end - start
        self.seg_num = seg_num
        self.manual_annot_coverage = 0
        self.detector_annot_coverage = 0
        self.seg_score = 0

    def annotation_in_segment(self,annotation_row):
        # for annotation to be in segment there are 3 cases:
            # 1. start_time <= annotation begin time < end_time
            # 2. start_time < annotation end time <= end_time
            # 3. annotation begin time <= start_time < annotation end time
        sel_begin_in_segment = ((self.start_time <= annotation_row["Begin Time (s)"]) and (annotation_row["Begin Time (s)"] < self.end_time))
        sel_end_in_segment = ((self.start_time < annotation_row["End Time (s)"]) and (annotation_row["End Time (s)"] <= self.end_time ))
        segment_in_sel = ((annotation_row["Begin Time (s)"] <= self.start_time) and (self.start_time < annotation_row["End Time (s)"]))
        sel_in_segment = sel_begin_in_segment or sel_end_in_segment or segment_in_sel
        return sel_in_segment
    
    def get_coverage_for_segment(self, annotation_row):
        annotation_start = annotation_row["Begin Time (s)"]
        annotation_end = annotation_row["End Time (s)"]
        
        if (self.start_time <= annotation_start):
            coverage_s = annotation_start
        else:
            coverage_s = self.start_time
        
        if (annotation_end <= self.end_time):
            converage_e = annotation_end
        else:
            converage_e = self.end_time
        
        coverage = converage_e - coverage_s
        return coverage

    def update_man_coverage(self, annotation_row):
        self.manual_annot_coverage += self.get_coverage_for_segment(annotation_row)

    def update_detector_coverage(self, annotation_row):
        self.detector_annot_coverage += self.get_coverage_for_segment(annotation_row)
