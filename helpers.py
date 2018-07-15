import datetime


def get_bucket_start_from_epoch(epoch):
    epoch_dt = datetime.datetime.utcfromtimestamp(epoch)
    epoch_dt_rounded = epoch_dt.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
    return epoch_dt_rounded


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
