
class BaseFiles:
    """
    Base Class for files used by detectors.

    Parameters
    ----------
    root_dir : String
        The full path to the directory storing the files.
    months : list or array-like
        The list of months the files cover.
    days : list or array-like
        The list of days the files cover.
    hours : list, array-like, default None
        The list of hours the files cover. If None use standard recorded hours
    year : String, default '2023'
        The year the files cover.
    extra : dict or None, default None
        If there are any extra selections to add to the array that do not involve all the hours in hours parameter.
        Must include months, days, and hours.
    """
    
    FILE_LENGTH = 600 # seconds 

    def __init__(self, root_dir, months, days, hours=None, year='2023', extra=None, site='06', dep='001', totalfiles=None, files_list=None) -> None:
        self.root_dir = root_dir
        self.months = months
        self.days = days
        self.year = year
        self.extra = extra
        if hours is None:
            self.hours = ['000000','050000','053000','060000','063000','070000','073000','120000',
            '163000','170000','173000','180000','183000','190000','193000','200000']
        else:
            self.hours = hours
        
        self.filenumber = 0
        if totalfiles is None:
            self.total_files = self.get_total_files()
        else:
            self.total_files = totalfiles
        self.site = site
        self.dep = dep
        if files_list is None:
            self.files_list = self.get_files()
        else:
            self.files_list = files_list
        
    
    def update_filenumber(self):
        self.filenumber += 1
    
    def reset_filenumber(self):
        self.filenumber = 0

    def get_files(self, extra=False):
        raise NotImplementedError(
            'get_files method not implemented in derived class'
        )
    
    def get_total_files(self):
        total_files = len(self.months) * len(self.days) * len(self.hours)
        if self.extra is not None:
            total_files += len(self.extra['months']) * len(self.extra['days']) * len(self.extra['hours'])
        return total_files
    
__all__ = ['AudioFiles', 'SelectionFiles','ManualFiles']