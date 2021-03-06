import os
import sys
import logging
import errno
import os.path as osp

import torch


def mkdir_if_missing(directory):
    if not osp.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


def check_isfile(path):
    isfile = osp.isfile(path)
    if not isfile:
        print("=> Warning: no file found at '{}' (ignored)".format(path))
    return isfile


def setup_logger(name, distributed_rank=0, save_dir='logs'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if distributed_rank == 0 and not logger.handlers:
        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(
            logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(ch)

        fh = logging.FileHandler(
            os.path.join("logs", "log.txt"), mode='a')
        fh.setLevel(logging.INFO)
        fh.setFormatter(
            logging.Formatter(
                "%(asctime)s %(name)s %(levelname)s: %(message)s"))
        logger.addHandler(fh)
    else:
        logging.disable(logging.CRITICAL)

    return logger


def clamp(input, min=None, max=None):
    ndim = input.ndimension()
    if min is None:
        pass
    elif isinstance(min, (float, int)):
        input = torch.clamp(input, min=min)
    elif isinstance(min, torch.Tensor):
        if min.ndimension() == ndim - 1 and min.shape == input.shape[1:]:
            input = torch.max(input, min.view(1, *min.shape))
        else:
            assert min.shape == input.shape
            input = torch.max(input, min)
    else:
        raise ValueError("min can only be None | float | torch.Tensor")

    if max is None:
        pass
    elif isinstance(max, (float, int)):
        input = torch.clamp(input, max=max)
    elif isinstance(max, torch.Tensor):
        if max.ndimension() == ndim - 1 and max.shape == input.shape[1:]:
            input = torch.min(input, max.view(1, *max.shape))
        else:
            assert max.shape == input.shape
            input = torch.min(input, max)
    else:
        raise ValueError("max can only be None | float | torch.Tensor")
    return input


class HiddenPrints:
    def __init__(self, activated=True):
        # activated??????????????????????????????????????????
        self.activated = activated
        self.original_stdout = None

    def open(self):
        sys.stdout.close()
        sys.stdout = self.original_stdout

    def close(self):
        self.original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        # ?????????os.devnull???????????????Linux???????????????/dev/null???
        # /dev/null?????????????????????????????????????????????????????????????????????????????????
        # ????????????/dev/null???sys.stdout????????????????????????

    def __enter__(self):
        if self.activated:
            self.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.activated:
            self.open()
