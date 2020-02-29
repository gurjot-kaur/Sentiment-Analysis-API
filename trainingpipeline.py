
from __future__ import absolute_import, division, print_function, unicode_literals
from metaflow import FlowSpec, step, retry, catch, batch, IncludeFile, Parameter, conda, conda_base,S3

def get_python_version():

    import platform
    versions = {'3' : '3.7.4'}
    return versions[platform.python_version_tuple()[0]]


@conda_base(python=get_python_version())
class TrainingFlow(FlowSpec):

    @conda(libraries={'pandas' : '1.0.1', 'tensorflow':'2.0.0','tensorflow-hub':'0.7.0','s3fs':'0.4.0','numpy':'1.17.2','scikit-learn':'0.22.1','keras':'2.3.1'})
    @step
    def start(self):

        import numpy as np
        import pandas as pd
        import tensorflow as tf
        import tensorflow_hub as hub

        df=pd.read_csv('labelled_clean.csv')

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

        train_Sentence_batch, train_Score_batch = next(iter(train.batch(6925)))

        embedding = "https://tfhub.dev/google/universal-sentence-encoder/4"


        hub_layer = hub.KerasLayer(embedding, input_shape=[],
                           dtype=tf.string, trainable=True)
        hub_layer(train_Sentence_batch[:])

        model = tf.keras.Sequential()
        model.add(hub_layer)
        model.add(tf.keras.layers.Dense(32, activation='relu'))
        model.add(tf.keras.layers.Dense(1))

        model.compile(optimizer='adam',
              loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
              metrics=['accuracy'])

        history = model.fit(train.shuffle(10000).batch(260),
                    epochs= 2,
                    validation_data=validation.batch(260), verbose = 1)

        results = model.evaluate(test.batch(260), verbose=1)

        tf.saved_model.save(model, "/Users/sid/Desktop/model/2/")



        self.next(self.end)
    @step
    def end(self):
        """
        End the flow.
        """
        pass

if __name__ == '__main__':
    TrainingFlow()
