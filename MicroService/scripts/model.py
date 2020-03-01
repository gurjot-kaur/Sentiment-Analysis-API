from __future__ import absolute_import, division, print_function, unicode_literals
import os
import re
from pathlib import Path
import logging
import joblib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import boto3

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_datasets as tfds
from metaflow import S3
import csv
from sklearn.model_selection import train_test_split
import functools
from tensorflow.keras import layers



DEFAULT_CONFIG_PATH = "/app/experiment_configs/default.yaml"

logger = logging.getLogger(__name__)


def run_pipeline():
    """ runs pipeline to train keras DNN model
        for sentiment classification """

    df = pd.read_csv('labelled_clean.csv')
    train, validation, test = np.split(df.sample(frac=1), [int(.7*len(df)), int(.8*len(df))])

    train = (
       tf.data.Dataset.from_tensor_slices(
        (
        train['Sentence'].values,
        train['Score'].values
        )
       )
    )

    validation = (
       tf.data.Dataset.from_tensor_slices(
        (
        validation['Sentence'].values,
        validation['Score'].values
        )
      )
    )

    test = (
       tf.data.Dataset.from_tensor_slices(
        (
        test['Sentence'].values,
        test['Score'].values
        )
      )
    )
    encoder = hub.load('https://tfhub.dev/google/universal-sentence-encoder/4')

    train_Sentence_batch, train_Score_batch = next(iter(train.batch(6925)))
    train_Sentence_batch


    model = tf.keras.models.Sequential()
    model.add(hub.KerasLayer('https://tfhub.dev/google/universal-sentence-encoder/4',
                input_shape=[],
                dtype=tf.string,
                trainable=True))

    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

    model.compile(optimizer='adam',
      loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
      metrics=['accuracy'])

    history = model.fit(train.shuffle(10000).batch(260),
                    epochs= 30,
                    validation_data=validation.batch(260),
                    verbose = 1)

    #print (model.predict(["we are bad"]))

    # Test
    results = model.evaluate(test.batch(260), verbose=1)

    for name, value in zip(model.metrics_names, results):
        logger.info("%s: %.3f" % (name, value))

    # Save
    model_name = config["model"]["name"]
    save_path = os.path.join(config["experiment"]["output_dirname"], f"{model_name}.keras")
    model.save(save_path)
    logger.info(f"Saved keras pipeline model at {save_path}")

    # Load & Check Consistency
    checkpoint = load_keras_hub_model(save_path)
    check_data = test.batch(512)
    assert np.all(
        checkpoint.predict(check_data) == model.predict(check_data)
    )
    logger.info("Keras saved model passed consistency check")

def load_keras_hub_model(save_path):
    return tf.keras.models.load_model(save_path,
        custom_objects={'KerasLayer': hub.KerasLayer}
    )

if __name__ == "__main__":
    run_pipeline()
