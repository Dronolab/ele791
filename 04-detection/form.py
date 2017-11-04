#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Convolutional network applied to the dronoset dataset classification task.
"""
import os
import glob
import argparse
import time

# Data loading and preprocessing
from dronoset import extract


def main(options):
    import tflearn
    from tflearn.data_utils import shuffle, to_categorical
    from tflearn.layers.core import input_data, dropout, fully_connected
    from tflearn.layers.conv import conv_2d, max_pool_2d
    from tflearn.layers.estimator import regression
    from tflearn.data_preprocessing import ImagePreprocessing
    from tflearn.data_augmentation import ImageAugmentation

    CHECKPOINT_BASENAME = 'dronoset_model.tfl'

    def maybe_load():
        options = [glob.glob(CHECKPOINT_BASENAME + f) for f in
                   ['.best*', '*', '.ckpt*']]
        files = [item for val in options for item in val]
        if files:
            ckpt = os.path.realpath(files[0]).split('.')
            ckpt.pop()
            ckpt = '.'.join(ckpt)
            return ckpt
        else:
            return None

    # Convolutional network building
    def create_model(input_shape, num_classes):

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
        model = tflearn.DNN(network,
                            checkpoint_path=CHECKPOINT_BASENAME + '.ckpt',
                            best_checkpoint_path=CHECKPOINT_BASENAME + '.best',
                            best_val_accuracy=0.9,
                            tensorboard_verbose=0)
        return model

    def train_model(model, n_epochs, ckpt_name='model.tfl'):
        run_id = int(time.time())
        (X, Y) = extract.load_data()
        (X, Y) = shuffle(X, Y)
        Y = to_categorical(Y, len(extract.SHAPE_LABELS))

        model.fit(X, Y,
                  n_epoch=n_epochs, shuffle=True,
                  show_metric=True, batch_size=96,
                  validation_set=0.1,
                  snapshot_epoch=True,
                  snapshot_step=500,
                  run_id='%d_dronoset_cnn' % run_id)

        model.save(ckpt_name)

    # Main starts here
    model = create_model([None, 32, 32, 3], 14)
    ckpt = maybe_load()

    if options.subparser == 'train':
        if ckpt and options.load:
            print('Loading pretrained model file: %s' % ckpt)
            model.load(ckpt)
        ckpt_name = 'dronoset_model.tfl'
        train_model(model, options.n_epochs, ckpt_name)
        print('model final checkpoint file is', ckpt_name)
    if options.subparser == 'eval':
        if not ckpt:
            raise Exception('cannot evaluate untrained model')
        model.load(ckpt)
        sample = extract.load_sample(options.file, options.show)
        pred = model.predict(sample)
        print(extract.unpack(pred))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Command line interface for "
                                                 "Dronolab's form classifier")
    subparsers = parser.add_subparsers(dest='subparser', metavar='CMD')

    # train subparser
    parser_train = subparsers.add_parser('train', help='train model')
    parser_train.add_argument('--no-load', dest='load', action='store_false',
                              help='do not load model from file')
    parser_train.add_argument('-n', '--n-epochs', type=int, default=100,
                              help='set number of epochs for fitting')

    # eval subparser
    parser_eval = subparsers.add_parser('eval', help='evaluate single image')
    parser_eval.add_argument('file')
    parser_eval.add_argument('--show', action='store_true',
                             help='open image being evaluated')

    options = parser.parse_args()
    if not options.subparser:
        parser.parse_args(['--help'])

    print(options)
    main(options)
