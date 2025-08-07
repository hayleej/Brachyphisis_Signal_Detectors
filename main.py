from utils.filesystem import selectionfiles, audiofiles
from utils import score
from detectors import envelope, correlate

def get_detections(model_name, months, days,extra, site='06',dep='001'):
    '''
    Get the katydid detection using a given analytical detector

    Parameters
    ----------
    model_name : string
        Name of the model/detector
    months : list[str]
        The list of months the files cover.
    days : bool, default False
        The list of days the files cover.
    extra : dict or None
        If there are any extra selections to add to the array that do not involve all the hours in standard recorded hours.
        Must include months, days, and hours.
    site : string
        The site number. Used for accessing the correct audio file.
    dep : string
        The deployment number. Used for accessing the correct audio file.

    '''

    # detector = correlate or envelope
    write_file = f"Brachyphisis_Signal_Detectors/Data/Site{site}_Deployment{dep}_selections_{model_name}.txt"
    
    # get the audio files from the site and deployment
    rootdir = f"Brachyphisis_Signal_Detectors/Data/site{site}/deployment_{dep}"
    audio_files = audiofiles.AudioFiles(rootdir,months,days,hours=None,year='2023',extra=extra, site=site, dep=dep)
    
    if model_name == 'envelope':
        # initialise envelope detector with Butterworth high-pass filter of 17 kHz
        detector = envelope.EnvelopeDetector(audio_files,filter_cutoff_freq=17000,max_interval_length=10000,min_disyllabic_len=5000,lower_faint=0.002,lower_loud=0.003, write_path=write_file)
    else:
        # correlation detector
        template_name = "Brachyphisis_Signal_Detectors/Data/site06/deployment_001/6_20230327_053000.wav"
        # initialise correlation detector with Butterworth high-pass filter of 17 kHz
        # use template_name as the template of the katydid signal to correlate audio to
        detector = correlate.CorrelateDetector(audio_files,template_name,template_end_time=0.225,filter_cutoff_freq=17000,max_interval_length=12000,min_disyllabic_len=5000, write_path=write_file)
    
    # detect katydid and output detections to write_file
    detector.detect()


def get_scores_and_cm_detect(model_name, months, days, extra):
    '''
    Calculate precision and recall scores and confusion matrix for a given analytical detector

    Parameters
    ----------
    model_name : string
        Name of the model
    months : list[str]
        The list of months the files cover.
    days : bool, default False
        The list of days the files cover.
    extra : dict or None
        If there are any extra selections to add to the array that do not involve all the hours in standard recorded hours.
        Must include months, days, and hours.

    '''
    # detector = correlate or envelope
    if model_name == 'correlate':
        rootdir = f"Brachyphisis_Signal_Detectors/Data"
        detector_file = f"Site06_Deployment001_selections_{model_name}.txt"
    elif model_name == "envelope":
        rootdir = f"Brachyphisis_Signal_Detectors/Data"
        detector_file = f"Site06_Deployment001_selections_{model_name}.txt"
    else:
        raise ValueError("Did not specify correlate or envelope")

    # get the files containing the annotations of katydids made by the analytical detector
    selections = selectionfiles.ManualFiles(rootdir,months,days,hours=None,year='2023',extra=extra, site='06', dep='001',manual_file_path=detector_file)

    # get the files containing the annotations of katydids manually made by researcher using RavenPro
    manual_filepath = "manual_selection_dep001.txt"
    manual_root = "Brachyphisis_Signal_Detectors/Data"
    manual_selections = selectionfiles.ManualFiles(manual_root,months,days,hours=None,year='2023',extra=extra, site='06', dep='001',manual_file_path=manual_filepath)

    segment_length = 1 # second length segments to split file into
    write_file = f"Brachyphisis_Signal_Detectors/Data/SCORE{segment_length}_Site06_Deployment001_{model_name}"

    myscores = score.SCORE(selections, manual_selections, model_name, seg_length=segment_length)
    scores = myscores.scores_for_model(write_file)
    myscores.confusion_matrix()

def run():
    # list of days and hours the files contain
    months=[]
    days=[]
    extra = {'months': ['03'], 'days':['16','17','18'], 'hours':['000000','050000','053000'], 'year':'2023'}

    # run correlate detector on files
    print("Running Correlation Detector")
    get_detections('correlate',months,days,extra,site='06',dep='001')
    
    # run envelope detector on files
    print("Running Envelope Detector")
    get_detections('envelope',months,days,extra,site='06',dep='001')

    # score correlate
    get_scores_and_cm_detect('correlate',months,days,extra)

    # score envelope
    get_scores_and_cm_detect('envelope',months,days,extra)


if __name__ == "__main__":
    # run the files
    run()


