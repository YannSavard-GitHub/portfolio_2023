
"""
Project: Adaptive Rhythmic Training Application (ARTA)
File   : neuralnetwork.py
Date   : 21/01/2022
Author : Yann Savard

This code is open source, except for some parts that were taken
from external sources and their sources are mentioned in the code.

History: programmed from september 2021 to february 2022 as part of my bachelor project:
"Conception and Evaluation of New Rhythm-Based Dexterity Training Methods with Adaptive Game Mechanics and AI"
"""

#source: Classify Images Using Python & Machine Learning - https://www.youtube.com/watch?v=iGWbqhdjf2s

import tensorflow as tf
from tensorflow import keras

from keras.models import Sequential, save_model, load_model
from keras.layers import Dense, Flatten, Conv2D, MaxPooling2D, Dropout, LSTM, Bidirectional, Conv1D
from keras.layers import Lambda, Reshape, Permute, Input, add, Conv3D, GaussianNoise, concatenate
from keras.layers import ConvLSTM2D, BatchNormalization, TimeDistributed, Add, Activation, GaussianNoise

from tensorflow.keras import layers
from tensorflow.python.keras.callbacks import TensorBoard


from time import time
from tensorflow.keras.utils import to_categorical
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from keras.datasets import mnist

import os
import random as rnd

os.environ['KMP_DUPLICATE_LIB_OK']='True' # to avoid error 15:

class NeuralNetwork():
	def __init__(self, g_manager):
		self.gm= g_manager
		self.pm = None
		self.tensorboard=None
		self.model=None

		#data set
		self.split_ratio = 0.0
		self.x_train=[]
		self.x_test=[]
		self.y_train=[]
		self.y_test=[]

		# optimization of rhythmic patterns
		self.truth = []

		self.best_acc_x = []
		self.best_acc_y = []

		self.best_perf_x = []
		self.best_perf_y = []

		self.best_bpm_x = []
		self.best_bpm_y = []

		#tensorboard
		self.writer=None
		self.training_log_dir = None

		#training history
		self.hist=[]


		#hyper-parameters of the neural network
		self.hidden_layers=0
		self.batch_size=0
		self.learning_rate=0.0
		self.decay= 0.0
		self.epochs=0
		self.validation_split=0.0


	def set_tensorboard_cnn(self):
		"""Sets tensorboard and compiles the neural network. NOTE: tensorboard is not functional in this version.
		The history of training of the model is shown in the method self.evaluate_model instead of tensorboard."""
		self.set_tensorboard()
		self.set_compile_neural_network()


	def set_tensorboard(self):
		"""Sets tensorboard adn the training_log_dir.""" # source:
		self.tensorboard= TensorBoard(log_dir="Logs/{}".format(time()))
		self.training_log_dir = os.path.join(self.tensorboard.log_dir, 'training')
		self.writer= tf.summary.create_file_writer(self.training_log_dir)


	def split_data_set(self, factor):
		"""Splits the self.pm.all_data_x and self.pm.all_data_y data sets into training and validation sets for
		the neural network, according to ratio given in parameter (factor)"""

		self.pm= self.gm.perf_manager
		self.split_ratio=factor

		x_set = self.pm.all_data_x
		y_set = self.pm.all_data_y
		print("Total data: ", len(self.pm.all_data_y))

		#reshape x_set and add 3 arrays with 0.0 values on axis 1 to make the size (x_set.shape[0], 28,28)

		x_set = np.reshape(x_set, (x_set.shape[0], x_set.shape[1],x_set.shape[2]))
		x_new_shape=(x_set.shape[0], 28, x_set.shape[2])
		new_x_set=np.zeros(x_new_shape)

		axis_one_shape = (28,28)
		axis_one = np.zeros(axis_one_shape)

		for i in range(x_set.shape[0]):
			for j in range(25):
				for k in range(28):
						axis_one[j + 3][k]=x_set[i][j][k]

			new_x_set[i] = axis_one
		x_set=new_x_set


		axis0_size_x = np.size(x_set, 0)
		axis0_size_y = np.size(y_set, 0)

		shape_x_train= (round(axis0_size_x * factor), 28, 28)
		shape_x_test=  (round(axis0_size_x - shape_x_train[0]), 28, 28)

		shape_y_train= (round(axis0_size_y * factor),28)
		shape_y_test=  (round(axis0_size_y - shape_y_train[0]),28)


		self.x_train= np.zeros(shape_x_train)
		print("Total x_train: ", self.x_train.shape[0])
		self.x_test= np.zeros(shape_x_test)
		print("Total x_test: ", self.x_test.shape[0])
		self.y_train = np.zeros(shape_y_train)
		print("Total y_train: ", len(self.y_train))
		self.y_test = np.zeros(shape_y_test)
		print("Total y_test: ", len(self.y_test))

		# x values
		for i in range(axis0_size_x - 1):
			for j in range(28):
				for k in range(28):
					factor1= round(axis0_size_x * factor)
					if i <= factor1 - 1:
						self.x_train[i]=x_set[i]
					else:
						self.x_test[i - factor1] = x_set[i]

		# y values
		for i in range(axis0_size_y - 1):
			factor1= round(axis0_size_y * factor)
			if i <= factor1 - 1:
				self.y_train[i] = y_set[i][:]
			else:
				self.y_test[i - factor1] = y_set[i][:]

		#set data sets with new shapes
		self.pm.all_data_x = x_set
		self.pm.all_data_y = y_set


	def adjust_data_values(self):
		"""Method to manually modify specific values of the data sets. (Not used in this final version)"""
		for i in range(self.x_train.shape[0]):
			for j in range(28):
				# self.x_train[i][j][11] = min(self.x_train[i][j][11] * 1.0, 1.0)
				# self.x_train[i][j][12] = min(self.x_train[i][j][12] * 1.0, 1.0)
				# self.x_train[i][j][13] = min(self.x_train[i][j][13] * 1.0, 1.0)
				# self.x_train[i][j][14] = min(self.x_train[i][j][14] * 1.0, 1.0)
				# self.x_train[i][j][15] = min(self.x_train[i][j][15] * 1.0, 1.0)
				# self.x_train[i][j][16] = min(self.x_train[i][j][16] * 1.0, 1.0)
				# self.x_train[i][j][17] = min(self.x_train[i][j][17] * 1.0, 1.0)
				# self.x_train[i][j][18] = min(self.x_train[i][j][18] * 1.0, 1.0)
				# self.x_train[i][j][19] = min(self.x_train[i][j][19] * 1.0, 1.0)
				# self.x_train[i][j][20] = min(self.x_train[i][j][20] * 1.0, 1.0)
				# self.x_train[i][j][21] = min(self.x_train[i][j][21] * 1.0, 1.0)
				# self.x_train[i][j][22] = min(self.x_train[i][j][22] * 1.0, 1.0)
				# self.x_train[i][j][23] = min(self.x_train[i][j][23] * 1.0, 1.0)
				# self.x_train[i][j][24] = min(self.x_train[i][j][24] * 1.0, 1.0)
				# self.x_train[i][j][25] = min(self.x_train[i][j][25] * 1.0, 1.0)
				# self.x_train[i][j][26] = min(self.x_train[i][j][26] * 1.0, 1.0)
				self.x_train[i][j][27] = self.x_train[i][j][27] * 0.3

		for i in range(len(self.y_train)):
			# self.y_train[i][11] = min(self.y_train[i][11] * 1.0, 1.0)
			# self.y_train[i][12] = min(self.y_train[i][12] * 1.0, 1.0)
			# self.y_train[i][13] = min(self.y_train[i][13] * 1.0, 1.0)
			# self.y_train[i][14] = min(self.y_train[i][14] * 1.0, 1.0)
			# self.y_train[i][15] = min(self.y_train[i][15] * 1.0, 1.0)
			# self.y_train[i][16] = min(self.y_train[i][16] * 1.0, 1.0)
			# self.y_train[i][17] = min(self.y_train[i][17] * 1.0, 1.0)
			# self.y_train[i][18] = min(self.y_train[i][18] * 1.0, 1.0)
			# self.y_train[i][19] = min(self.y_train[i][19] * 1.0, 1.0)
			# self.y_train[i][20] = min(self.y_train[i][20] * 1.0, 1.0)
			# self.y_train[i][21] = min(self.y_train[i][21] * 1.0, 1.0)
			# self.y_train[i][22] = min(self.y_train[i][22] * 1.0, 1.0)
			# self.y_train[i][23] = min(self.y_train[i][23] * 1.0, 1.0)
			# self.y_train[i][24] = min(self.y_train[i][24] * 1.0, 1.0)
			# self.y_train[i][25] = min(self.y_train[i][25] * 1.0, 1.0)
			# self.y_train[i][26] = min(self.y_train[i][26] * 1.0, 1.0)
			self.y_train[i][27] = self.y_train[i][27] * 0.3

		for i in range(self.x_test.shape[0]):
			for j in range(28):
				# self.x_test[i][j][11] = min(self.x_test[i][j][11] * 1.0, 1.0)
				# self.x_test[i][j][12] = min(self.x_test[i][j][12] * 1.0, 1.0)
				# self.x_test[i][j][13] = min(self.x_test[i][j][13] * 1.0, 1.0)
				# self.x_test[i][j][14] = min(self.x_test[i][j][14] * 1.0, 1.0)
				# self.x_test[i][j][15] = min(self.x_test[i][j][15] * 1.0, 1.0)
				# self.x_test[i][j][16] = min(self.x_test[i][j][16] * 1.0, 1.0)
				# self.x_test[i][j][17] = min(self.x_test[i][j][17] * 1.0, 1.0)
				# self.x_test[i][j][18] = min(self.x_test[i][j][18] * 1.0, 1.0)
				# self.x_test[i][j][19] = min(self.x_test[i][j][19] * 1.0, 1.0)
				# self.x_test[i][j][20] = min(self.x_test[i][j][20] * 1.0, 1.0)
				# self.x_test[i][j][21] = min(self.x_test[i][j][21] * 1.0, 1.0)
				# self.x_test[i][j][22] = min(self.x_test[i][j][22] * 1.0, 1.0)
				# self.x_test[i][j][23] = min(self.x_test[i][j][23] * 1.0, 1.0)
				# self.x_test[i][j][24] = min(self.x_test[i][j][24] * 1.0, 1.0)
				# self.x_test[i][j][25] = min(self.x_test[i][j][25] * 1.0, 1.0)
				# self.x_test[i][j][26] = min(self.x_test[i][j][26] * 1.0, 1.0)
				self.x_test[i][j][27] = self.x_test[i][j][27] * 0.3

		for i in range(len(self.y_test)):
			# self.y_test[i][11] = min(self.y_test[i][11] * 1.0, 1.0)
			# self.y_test[i][12] = min(self.y_test[i][12] * 1.0, 1.0)
			# self.y_test[i][13] = min(self.y_test[i][13] * 1.0, 1.0)
			# self.y_test[i][14] = min(self.y_test[i][14] * 1.0, 1.0)
			# self.y_test[i][15] = min(self.y_test[i][15] * 1.0, 1.0)
			# self.y_test[i][16] = min(self.y_test[i][16] * 1.0, 1.0)
			# self.y_test[i][17] = min(self.y_test[i][17] * 1.0, 1.0)
			# self.y_test[i][18] = min(self.y_test[i][18] * 1.0, 1.0)
			# self.y_test[i][19] = min(self.y_test[i][19] * 1.0, 1.0)
			# self.y_test[i][20] = min(self.y_test[i][20] * 1.0, 1.0)
			# self.y_test[i][21] = min(self.y_test[i][21] * 1.0, 1.0)
			# self.y_test[i][22] = min(self.y_test[i][22] * 1.0, 1.0)
			# self.y_test[i][23] = min(self.y_test[i][23] * 1.0, 1.0)
			# self.y_test[i][24] = min(self.y_test[i][24] * 1.0, 1.0)
			# self.y_test[i][25] = min(self.y_test[i][25] * 1.0, 1.0)
			# self.y_test[i][26] = min(self.y_test[i][26] * 1.0, 1.0)
			self.y_test[i][27] = self.y_test[i][27] * 0.3


	def set_compile_neural_network(self):
		"""Sets and compiles the bilateral LSTM neural network and its hyper-parameters """
		# set model compile parameters

		# hidden layers formula to start with:
		# source:https://towardsdatascience.com/choosing-the-right-hyperparameters-for-a-simple-lstm-using-keras-f8e9ed76f046

		# Nh= Nₛ / (a * (Nᵢ + Nₒ)
		# Nᵢ is the number of input neurons, Nₒ the number of output neurons,
		# Nₛ the number of samples in the training data, and α represents a
		# scaling factor that is usually between 2 and 10.

		self.hidden_layers = int(round(self.x_train.shape[0] / (4 * (28 + 28))))  # day 6: factor= 6

		self.validation_split = self.split_ratio
		self.batch_size = 192

		self.epochs = (round((self.x_train.shape[0]) / self.batch_size) - 1)

		self.learning_rate = 0.012 #initial rate 0.001
		self.decay = self.learning_rate / self.epochs  # source of formula: https://towardsdatascience.com/learning-rate-schedule-in-practice-an-example-with-keras-and-tensorflow-2-0-2f48b2888a0c#:~:text=The%20constant%20learning%20rate%20is,pass%20the%20argument%20learning_rate%3D0.01%20.

		#source: Sentdex - https://www.youtube.com/watch?v=BSpXCRTOLJA - shape

		self.model = Sequential()
		self.model.add(Bidirectional(LSTM(self.hidden_layers, input_shape=(self.x_train.shape[1:]), return_sequences=False)))
		# self.model.add(GaussianNoise(0.15))  # to add robustness to the model.
		self.model.add(Dropout(0.4)) # to add randomness and diminish overfitting.
		self.model.add(Dense(28, activation='relu'))

		opt = tf.keras.optimizers.Adam(lr=self.learning_rate, decay=self.decay) #day 6 learning rate: 0.001  - decay: decay=1e-6
		self.model.compile(loss= 'mse', optimizer=opt, metrics=['accuracy'])


	def save_model(self):
		"""Saves the model to the path 'Neural_Network_Models/model'. """
		# Save the model
		filepath = 'Neural_Network_Models/model'
		save_model(self.model, filepath)

	def load_model(self):
		"""Loads the model from the path 'Neural_Network_Models/model'. """
		# Load the model
		filepath = 'Neural_Network_Models/model'
		self.model = load_model(filepath, compile=True)

	def compare_pred_true(self):
		"""Compares predictions of the neural network with the ground truth (y data sets:
		self.y_train and self.y_test). Displays the results as np.array images. """

		shape_x = (384, 28 * 4, 1)
		array_y = np.zeros(shape_x)

		#training
		predictions = self.model.predict(self.x_train[-385:-1])
		pred_idx=0
		for c in range(4):
			idx = c * 28
			for r in range(0, 384, 4):
				#convert arrays into images
					for i in range(28):
						array_y[r][i + idx]=predictions[pred_idx][i] # prediction
						array_y[r + 1][i + idx]=self.y_train[pred_idx][i] # ground truth
						array_y[r + 2][i + idx] = self.x_train[pred_idx][-1][i]  # x_test last array
						# to make a space between the groups of 3 arrays (for visual representation purpose)
						array_y[r + 3][i + idx] = 0.0
					pred_idx += 1
		plt.imshow(array_y)
		plt.show()


		#test
		predictions = self.model.predict(self.x_test[-385:-1])
		pred_idx = 0
		for c in range(4):
			idx = c * 28
			for r in range(0, 384, 4):
				# convert arrays into images
				for i in range(28):
					array_y[r][i + idx] = predictions[pred_idx][i]  # prediction
					array_y[r + 1][i + idx] = self.y_test[pred_idx][i]  # ground truth
					array_y[r + 2][i + idx] = self.x_test[pred_idx][-1][i]  # x_test last array
					# to make a space between the groups of 3 arrays (for visual representation purpose)
					array_y[r + 3][i + idx] = 0.0
				pred_idx += 1
		plt.imshow(array_y)
		plt.show()

	def optimize_patterns(self, parameter, patterns_x, patterns_y, idx_begin, number, iterations):
		"""
		Optimizes rhythmic patterns using the neural network to predict half-pattern average performance of randomly
		generated rhythmic patterns. This process is repeted the specified number of times (iterations).

		:param parameter: parameter to optimize - (in the final version, only parameter 11 is used, the
		 				  average performance of half-patterns.
		:param patterns_x: list of x data set indexes with rhythmic patterns that have the best average performance
						   values (parameter 11)
		:param patterns_y: list of y data set indexes associated with the patterns_x.
		:param idx_begin: first index to optimize in the patterns_x and patterns_y lists
		:param number: the number of indexes to optimize
		:param iterations: number of iterations of the optimization process.
		:return:
		"""

		best_pattern_x = []
		best_pattern_y = []

		opt_x_patterns=np.zeros((number * 6, 28, 1))
		#iterations
		iteration=0

		#mofify rhythmic patterns_x
		#---------------------------------------------------------------------------------------------------------------
		shape = (1, 28, 28)
		shape2= (28,)
		idx=0
		for i in range(0, number * 6, 6):

			#consider only indexes idx_begin to idx_end of the patterns
			if idx < idx_begin:
				idx +=1
				continue

			# x_train
			x_input=np.zeros(shape)
			x_input[0]=patterns_x[idx].copy()

			new_x_input = x_input.copy()

			best_pattern_x= x_input[0][-1].copy() # set initial x_input as the best pattern, until a better one is found

			# y_train
			self.truth = np.zeros(shape2)
			best_pattern_y= self.truth.copy()

			print("")
			print("Optimizing rhythmic pattern...")
			print("")

			for j in range(iterations):
				# new pattern_x----------------------------------------------------------
				# random rhythmic pattern
				rhythmic_pattern = self.gm.rhythm_manager.generate_random_half_pattern()
				#print(f"new rhythmic_pattern {i}-{j}= ", rhythmic_pattern)

				# x_input index 12= rhythmic_value - index 13 to 25= rhythmic values
				new_x_input[0][-1][12] = rhythmic_pattern[0]
				for k in range(12):
					new_x_input[0][-1][k + 12]=rhythmic_pattern[k]
				#------------------------------------------------------------------------

				#predictions - x_train
				predict_x= self.model.predict(np.array([patterns_x[idx]]))
				predict_x= np.reshape(predict_x, (predict_x.shape[1]))

				# predictions - new pattern (with random values)
				predict_new = self.model.predict(np.array(new_x_input))
				predict_new = np.reshape(predict_new, (predict_new.shape[1]))

				# verify if the parameters's predicted value is better then the the current one
				if predict_new[parameter] > predict_x[parameter] and \
						predict_new[parameter] > best_pattern_y[parameter]:                #changed: elif, not if!

					best_pattern_x = new_x_input[0][-1].copy()
					best_pattern_y = predict_new.copy()
					#print("rhythmic_pattern= ", rhythmic_pattern)
					print(f"best x -> Iteration {j}= ", best_pattern_x)
			print(f"---------------------------------------------------------------------------------self.best_pattern_x {i} - end= ", best_pattern_x)

			for k in range(28):
				opt_x_patterns[i + 0][k] = best_pattern_y[k]
				opt_x_patterns[i + 1][k] = best_pattern_x[k]

				opt_x_patterns[i + 2][k] = predict_x[k]
				opt_x_patterns[i + 3][k] = patterns_y[idx][k]
				opt_x_patterns[i + 4][k] = patterns_x[idx][-1][k]

				opt_x_patterns[i + 5][k] = 0.0

			print(idx, ": ", patterns_y[idx][parameter], "-", predict_x[parameter], "-", best_pattern_y[parameter])
			print("*******************************************")

			idx += 1
			iteration +=1

			if iteration == number:
				break

		plt.imshow(opt_x_patterns)
		plt.show()


	def train_model(self):
		"""Trains the neural network with the current data set (self.x_train and self.y_train)."""
		#tensorboard - not used in this version (needs to be adapted in future versions)

		self.tensorboard= TensorBoard(log_dir="Logs/{}".format(time()))
		training_log_dir = os.path.join(self.tensorboard.log_dir, 'training')
		writer= tf.summary.create_file_writer(training_log_dir)

		# Train the model
		self.hist = self.model.fit(self.x_train, self.y_train,
								   batch_size=self.batch_size,
								   epochs= self.epochs,
								   validation_split=self.validation_split,
								   callbacks=[self.tensorboard])


	def evaluate_model(self):
		"""Evaluates the neural network with the test data set (self.x_test and self.y_test).
		Shows training history for the parameters 'accuracy'[training set], 'val_accuracy'[test set],
		'loss'[training set] and 'val_loss'[test set] """

		# Evaluate the model using test data set
		self.model.evaluate(self.x_test, self.y_test)[1]

		plt.style.use('fivethirtyeight')
		#source: https: // www.pluralsight.com / guides / data - visualization - deep - learning - model - using - matplotlib
		plt.plot(self.hist.history['accuracy'], 'g', label='Training accuracy')
		plt.plot(self.hist.history['val_accuracy'], 'b', label='Validation accuracy')
		plt.show()
		plt.plot(self.hist.history['loss'], 'g', label='Training loss')
		plt.plot(self.hist.history['val_loss'], 'b', label='Validation loss')
		plt.show()


"""
source: https://www.youtube.com/watch?v=2U6Jl7oqRkM
NOTE: To connect to the tensorboard page where graphics are shown, copy-paste the following in the terminal: 
	  tensorboard --logdir=log_dir
"""
