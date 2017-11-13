#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import glob
import argparse
import time

# Data loading and preprocessing
from dronoset import extract
from utils import resize_by_altitude, to_nptiles

import tflearn
from PIL import Image
from tflearn.data_utils import shuffle, to_categorical
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression

TILE_SHAPE = (32, 32, 3)
TILE_SIZE = TILE_SHAPE[0] * TILE_SHAPE[1] * TILE_SHAPE[2]


class Localizer(object):
    """ Localization module.

    This module is used to detect targets in an image by exploding the input
    into small tiles. The tiles are then feed through a DNN used to classify
    targets from grass.

    Arguments:
        shape: shape of the Deep Neural Network to generate.
        num_classes: number of output classes.
        auto_load: flags to indicate whether or not to pre-load a model.


    Attributes:
        model: refence to the neural network.
        checkpoint: filename used to load/save the model.

    """

    def __init__(self, shape, num_classes, auto_load=True):
        network = input_data(shape=[None, shape.pop(0)])
        for i in shape:
            network = fully_connected(network, i,
                                      activation='tanh',
                                      regularizer='L2',
                                      weight_decay=0.001)
            network = dropout(network, 0.8)

        network = fully_connected(network, num_classes, activation='softmax')
        network = regression(network,
                             optimizer='SGD',
                             loss='categorical_crossentropy',
                             learning_rate=0.001)
        self.model = tflearn.DNN(network, tensorboard_verbose=0)
        self.checkpoint = self._maybe_load('localization_model.tfl')

        if self.checkpoint and auto_load:
            print('Loading pretrained model file: %s' % self.checkpoint)
            self.model.load(self.checkpoint)

    def _maybe_load(self, basename):
        options = [glob.glob(basename + f) for f in
                   ['.best*', '*', '.ckpt*']]
        files = [item for val in options for item in val]
        if files:
            ckpt = os.path.realpath(files[0]).split('.')
            ckpt.pop()
            ckpt = '.'.join(ckpt)
            return ckpt
        else:
            return None

    def train(self, n_epochs, dataset):
        """ Train.

        Train model on dataset.

        """
        run_id = int(time.time())
        (X, Y) = dataset
        (X, Y) = shuffle(X, Y)
        n, w, h, c = X.shape
        X = np.reshape(X, (n, w*h*c))

        Y = to_categorical(Y, len(extract.TARGET_LABELS))

        self.model.fit(X, Y,
                       n_epoch=n_epochs, shuffle=True,
                       show_metric=True, batch_size=96,
                       validation_set=0.1,
                       snapshot_epoch=True,
                       snapshot_step=500,
                       run_id='%d_localization_DNN' % run_id)

        print('Saving model checkpoint file as: ', self.checkpoint)
        self.model.save(self.checkpoint)

    def eval(self, tiles):
        """ Eval.

        Evaluate samples.

        """
        # feed through model
        prediction = self.model.predict(tiles)
        print(prediction.shape, prediction[0])

        # FIXME: save to disk
        for i, p in enumerate(prediction):
            if p[0] >= 0.96:
                print('idx: {}, {}'.format(i, prediction[i]))
                resized.crop(boxes[i]).save('trash/auto-{}.jpg'.format(i))


def parse_commandline():
    parser = argparse.ArgumentParser(description="Command line interface for "
                                                 "Dronolab's target localizer")
    parser.add_argument('--no-load', dest='load', action='store_false',
                        help='do not load model from file')
    subparsers = parser.add_subparsers(dest='subparser', metavar='CMD')

    # train subparser
    parser_train = subparsers.add_parser('train', help='train model')
    parser_train.add_argument('-n', '--n-epochs', type=int, default=100,
                              help='set number of epochs for fitting')

    # eval subparser
    parser_eval = subparsers.add_parser('eval', help='evaluate single image')
    parser_eval.add_argument('file')
    parser_eval.add_argument('--show', action='store_true',
                             help='open image being evaluated')
    # run subparser
    parser_eval = subparsers.add_parser('run', help='continuously evaluate '
                                                    'ZMQ requests')

    options = parser.parse_args()
    if not options.subparser:
        parser.parse_args(['--help'])

    return options


if __name__ == '__main__':
    options = parse_commandline()
    loop = 1

    localizer = Localizer([TILE_SIZE, 1024, 100], 2, options.load)

    if options.subparser == 'train':
        dronoset = extract.load_data(target_only=True)
        localizer.train(options.n_epochs, dronoset)
    if options.subparser == 'eval':
        start = time.time()
        im = Image.open(options.file)
        resized = resize_by_altitude(im, altitude=50)
        tiles, boxes = to_nptiles(resized, (32, 32), 0.5)

        # convert to a single tensor
        n, w, h, c = tiles.shape
        tiles = np.reshape(tiles, (n, w*h*c))

        localizer.eval(tiles)
        end = time.time()
        print("full eval took: {}s".format(end-start))
    if options.subparser == 'run':
        while loop:
            print('waiting for a ZMQ')
            loop = 0
