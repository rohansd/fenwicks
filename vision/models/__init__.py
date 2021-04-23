import tensorflow as tf
#from keras import applications
import keras_applications
from tensorflow.python.keras import engine as keras_engine

keras_applications.set_keras_submodules(backend=tf.keras.backend, layers=tf.keras.layers, models=tf.keras.models,
                                        utils=tf.keras.utils, engine=keras_engine)
