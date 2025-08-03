from . import BaseFiles

class AudioFiles(BaseFiles):
    
    def __init__(self, root_dir, months, days, hours=None, year='2023', extra=None, site='06', dep='001', total_files=None, files_list=None) -> None:
        super().__init__(root_dir, months, days, hours, year, extra, site, dep, total_files,files_list)

    def get_files(self, extra=False):
        """
        Get a list of audio file paths.

        Parameters
        ----------
        extra : bool, default False
            True when using self.extra for the values. Otherwise, uses self.months, self.days, self.hours, etc.

        Returns
        -------
        list
            The list of audio file paths.
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

        audio_files_list = []
        for month in months:
            for day in days:
                for hour in hours:
                    new_sel_file = f'6_{year}{month}{day}_{hour}.wav'
                    audio_files_list.append(new_sel_file)
        
        if (not extra) and (self.extra is not None):
            extra_files = self.get_files(extra=True)
            audio_files_list.extend(extra_files)


        return audio_files_list