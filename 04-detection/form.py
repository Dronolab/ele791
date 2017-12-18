#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import argparse
import time

# Data loading and preprocessing
from dronoset import extract

import tflearn
from tflearn.data_utils import shuffle, to_categorical
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.estimator import regression
from tflearn.data_preprocessing import ImagePreprocessing
from tflearn.data_augmentation import ImageAugmentation


class Form(object):
    """ Form classification module.

    This module is used to classify targets in a cropped image.

    Arguments:
        shape: shape of the network
        num_classes: number of output classes
        auto_load: flags to indicate whether or not to pre-load a model.

    Attributes:
        model: refence to the neural network.
        checkpoint: filename used to load/save the model.
    """

    def __init__(self, input_shape, num_classes, auto_load=True):
        self.checkpoint = self._maybe_load('dronoset_model.tfl')

        # Real-time data preprocessing
        img_prep = ImagePreprocessing()
        img_prep.add_featurewise_zero_center()
        img_prep.add_featurewise_stdnorm()

        # Real-time data augmentation
        img_aug = ImageAugmentation()
        img_aug.add_random_flip_leftright()
        img_aug.add_random_rotation(max_angle=25.)

        # actual network
        network = input_data(shape=input_shape,
                             data_preprocessing=img_prep,
                             data_augmentation=img_aug)
        network = conv_2d(network, 32, 3, activation='relu')
        network = max_pool_2d(network, 2)
        network = conv_2d(network, 64, 3, activation='relu')
        network = conv_2d(network, 64, 3, activation='relu')
        network = max_pool_2d(network, 2)
        network = fully_connected(network, 512, activation='relu')
        network = dropout(network, 0.5)
        network = fully_connected(network, num_classes, activation='softmax')
        network = regression(network,
                             optimizer='adam',
                             loss='categorical_crossentropy',
                             learning_rate=0.001)
        self.model = tflearn.DNN(network,
                                 best_val_accuracy=0.9,
                                 tensorboard_verbose=0)

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
        Y = to_categorical(Y, len(extract.SHAPE_LABELS))

        self.model.fit(X, Y,
                       n_epoch=n_epochs, shuffle=True,
                       show_metric=True, batch_size=96,
                       validation_set=0.2,
                       snapshot_epoch=True,
                       snapshot_step=500,
                       run_id='%d_dronoset_cnn' % run_id)

        print('Saving model checkpoint file as: ', self.checkpoint)
        self.model.save(self.checkpoint)

    def eval(self, sample):
        pred = self.model.predict(sample)
        return extract.unpack(pred)


def parse_commandline():
    parser = argparse.ArgumentParser(description="Command line interface for "
                                                 "Dronolab's form classifier")
    parser.add_argument('--no-load', dest='load', action='store_false',
                        help='do not load model from file')
    subparsers = parser.add_subparsers(dest='subparser', metavar='CMD')

    parser_train = subparsers.add_parser('train', help='train model')
    parser_train.add_argument('-n', '--n-epochs', type=int, default=100,
                              help='set number of epochs for fitting')

    parser_eval = subparsers.add_parser('eval', help='evaluate single image')
    parser_eval.add_argument('file')
    parser_eval.add_argument('--show', action='store_true',
                             help='open image being evaluated')

    parser_run = subparsers.add_parser('run', help='continuously evaluate '
                                                   'ZMQ requests')
    parser_run.add_argument('--foo', action='store_true', help='dummy option')
    parser_test = subparsers.add_parser('test', help='used to test stuff')
    parser_test.add_argument('file')

    options = parser.parse_args()
    if not options.subparser:
        parser.parse_args(['--help'])

    return options


if __name__ == '__main__':
    options = parse_commandline()
    loop = 1

    form = Form([None, 32, 32, 3], 14, options.load)

    start = time.time()
    if options.subparser == 'train':
        dronoset = extract.load_data(target_only=True)
        form.train(options.n_epochs, dronoset)
    if options.subparser == 'eval':
        sample = extract.load_sample(options.file, options.show)
        out = form.eval(sample)
        print("prediction is :", out)
    if options.subparser == 'test':
        from utils import resize_by_altitude, to_nptiles
        from PIL import Image
        import numpy as np

        im = Image.open(options.file)
        resized, factor = resize_by_altitude(im, altitude=50, ppm=20)
        tiles, boxes = to_nptiles(resized, (32, 32), 0.5)

        data = np.empty(shape=(1, 32, 32, 3))
        out = []

        for i in tiles:
            data[0, :, :, :] = i
            out.append(form.eval(data))

    if options.subparser == 'run':
        while loop:
            print('waiting for a ZMQ')
            loop = 0
    end = time.time()
    print("full elapse took: {}s".format(end-start))
