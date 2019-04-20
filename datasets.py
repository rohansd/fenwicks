import tensorflow as tf
import os
from urllib.parse import urlparse

__all__ = ['URLs', 'untar_data']


class URLs:
    FASTAI = 'http://files.fast.ai/data/'
    DVC = f'{FASTAI}dogscats.zip'
    CIFAR10 = f'{FASTAI}cifar10.tgz'

    TF = 'http://download.tensorflow.org/'
    SPEECH_CMD_001 = f'{TF}data/speech_commands_v0.01.tar.gz'
    SPEECH_CMD_002 = f'{TF}data/speech_commands_v0.02.tar.gz'
    FLOWER_PHOTOS = f'{TF}example_images/flower_photos.tgz'

    KAGGLE_COMPETITION_DOWNLOAD = 'competitions download -c '
    KAGGLE_DATASETS_DOWNLOAD = 'datasets download -d '
    KAGGLE_CIFAR10 = f'{KAGGLE_COMPETITION_DOWNLOAD}cifar-10'
    KAGGLE_IMDB = f'{KAGGLE_COMPETITION_DOWNLOAD}word2vec-nlp-tutorial'
    KAGGLE_DIABETIC_RETINOPATHY = f'{KAGGLE_COMPETITION_DOWNLOAD}diabetic-retinopathy-detection'
    KAGGLE_CARDIAC_FUNCTION = '{KAGGLE_COMPETITION_DOWNLOAD}second-annual-data-science-bowl'
    KAGGLE_SKIN_CANCER = f'{KAGGLE_DATASETS_DOWNLOAD}kmader/skin-cancer-mnist-ham10000'
    KAGGLE_BONE_AGE = f'{KAGGLE_DATASETS_DOWNLOAD}kmader/rsna-bone-age'


def untar_data(url: str, dest: str = '.') -> str:
    if not os.path.isdir(dest):
        tf.gfile.MkDir(dest)
    url_path = urlparse(url).path
    fn = os.path.basename(url_path)
    data_dir = os.path.join(dest, 'datasets')
    if not tf.gfile.Exists(os.path.join(data_dir, fn)):
        tf.keras.utils.get_file(fn, origin=url, extract=True, cache_dir=dest)
    return data_dir
