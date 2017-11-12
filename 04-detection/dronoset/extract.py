import os
import sys
import numpy as np
import pickle
import zipfile
from PIL import Image
from progress.bar import Bar


SHAPE_LABELS = (
    'Circle',
    'Half Circle',
    'Quarter Circle',
    'Rectangle',
    'Trapezoid',
    'Triangle',
    'Cross',
    'Pentagon',
    'Hexagon',
    'Heptagon',
    'Octagon',
    'Star',
    'QRcode',
    'No Target'
)

TARGET_LABELS = (
    'Target',
    'No Target'
)

DIR = os.path.dirname(__file__)


def maybe_extract(archive='train_images.zip', workdir='dronoset'):
    if not os.path.isdir(workdir):
        os.mkdir(workdir)
        sources = zipfile.ZipFile(archive)
        sources.extractall(path=workdir)

    return os.path.join(workdir, 'train_images')


def pickle_dataset(filename, dataset):
    with open(filename, 'wb') as f:
        pickle.dump(dataset, f)


def maybe_unpickle(filename):
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            sys.stdout.write('Loading pickled dataset...')
            sys.stdout.flush()
            dataset = pickle.load(f)
            print('done')
    else:
        dataset = ([], [])

    return dataset


def load_data(target_only=False):
    X, Y = maybe_unpickle(os.path.join(DIR, 'dronoset.pickle'))

    if len(X) + len(Y) == 0:
        workdir = maybe_extract()
        image_paths = [os.path.join(workdir, f) for f in os.listdir(workdir)
                       if f.endswith('.jpg')]

        n = len(image_paths)
        X = np.empty(shape=(n, 32, 32, 3))
        Y = []

        bar = Bar('Extracting dronoset', max=n)
        for i in range(0, n):
            bar.next()

            path = image_paths[i]
            im = Image.open(path)
            X[i, :, :, :] = np.asarray(im)

            with open(path.replace('.jpg', '.txt')) as desc:
                Y.append(int(desc.read().split('\t')[1]))

        bar.finish()

        pickle_dataset('dronoset.pickle', (X, Y))

    if target_only:
        Y = [int(y == 13) for y in Y]

    return (X, Y)


def load_sample(filename, show=False):
    data = np.empty(shape=(1, 32, 32, 3))
    im = Image.open(filename)
    data[0, :, :, :] = np.asarray(im)
    if show:
        im.show()

    return data


def unpack(prediction):
    n = np.argmax(prediction)
    if len(prediction) > 2:
        return SHAPE_LABELS[n]
    else:
        return TARGET_LABELS[n]


if __name__ == '__main__':
    (x, y), (x_test, y_test) = load_data()
    foo = np.random.randint(0, 100)
    print('prediction: %d is %s' % (y[foo], SHAPE_LABELS[y[foo]]))
