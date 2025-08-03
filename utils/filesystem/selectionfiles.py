
from . import BaseFiles
import pandas as pd

class SelectionFiles(BaseFiles):
    def __init__(self, root_dir, months, days, hours=None, year='2023', extra=None, site='06', dep='001',total_files=None, files_list=None) -> None:
        super().__init__(root_dir, months, days, hours, year, extra, site, dep, total_files,files_list)

    def get_files(self, extra=False):
        """
        Get a list of selection file paths.

        Parameters
        ----------
        extra : bool, default False
            True when using self.extra for the values. Otherwise, uses self.months, self.days, self.hours, etc.

        Returns
        -------
        list
            The list of selection file paths.
        """
        
        if extra:
            months = self.extra['months']
            days = self.extra['days']
            hours = self.extra['hours']
            year = self.extra['year']
        else:
            months = self.months
            days = self.days
            hours = self.hours
            year = self.year

        selection_files_list = []
        for month in months:
            for day in days:
                for hour in hours:
                    new_sel_file = f'6_{year}{month}{day}_{hour}.selections.txt'
                    selection_files_list.append(new_sel_file)
        
        if (not extra) and (self.extra is not None):
            extra_files = self.get_files(extra=True)
            selection_files_list.extend(extra_files)


        return selection_files_list
    
    def combine_selection_files(self):
        self.reset_filenumber()
        selections = pd.read_csv(f"{self.root_dir}/{self.files_list[0]}",sep="\t",header=0)
        self.update_filenumber()
        for sel_file in self.files_list[1:]:
            df = pd.read_csv(f"{self.root_dir}/{sel_file}",sep="\t",header=0)
            df['Begin Time (s)'] = df['Begin Time (s)'] + (self.FILE_LENGTH * self.filenumber)
            df['End Time (s)'] = df['End Time (s)'] + (self.FILE_LENGTH * self.filenumber)
            self.update_filenumber()
            selections = pd.concat([selections, df], axis=0, ignore_index=True)
        self.reset_filenumber()
        selections = selections.sort_values(by='Begin Time (s)', ascending=True)
        print(f'Combined Selections, Final Selections have shape {selections.shape}')
        return selections
    

class ManualFiles(SelectionFiles):
    def __init__(self, root_dir, months, days, hours=None, year='2023', extra=None, site='06', dep='001',total_files=None, manual_file_path=None, files_list=None) -> None:
        if manual_file_path is not None:
            self.file_path = manual_file_path
        else:
            self.file_path = None
        super().__init__(root_dir, months, days, hours, year, extra, site, dep, total_files, files_list)
        

    def get_files(self, extra=False):
        """
        Get a list of selection file paths.

        Parameters
        ----------
        extra : bool, default False
            True when using self.extra for the values. Otherwise, uses self.months, self.days, self.hours, etc.

        Returns
        -------
        list
            The list of selection file paths.
        """
        if self.file_path is None:
            selection_files_list = super().get_files(extra)
        else:
            selection_files_list = []
            selection_files_list.append(self.file_path)

        return selection_files_list
    
    def combine_selection_files(self):
        self.reset_filenumber()
        selections = pd.read_csv(f"{self.root_dir}/{self.files_list[0]}",sep="\t",header=0)
        self.update_filenumber()
        for sel_file in self.files_list[1:]:
            df = pd.read_csv(f"{self.root_dir}/{sel_file}",sep="\t",header=0)
            df['Begin Time (s)'] = df['Begin Time (s)'] + (self.FILE_LENGTH * self.filenumber)
            df['End Time (s)'] = df['End Time (s)'] + (self.FILE_LENGTH * self.filenumber)
            self.update_filenumber()
            selections = pd.concat([selections, df], axis=0, ignore_index=True)
        self.reset_filenumber()
        selections = selections.sort_values(by='Begin Time (s)', ascending=True)
        print(f'Combined Selections, Final Selections have shape {selections.shape}')
        return selections
 