'''
this code is for supervised learning the state-action pair
using the neural network approach
'''
from __future__ import print_function
import tensorflow as tf

import numpy as np
import random
import pickle
import matplotlib.pyplot as plt
import argparse
import math
import time
import gzip
from env_test import Reacher



save_file='./model.ckpt'
data_file = open("data4.p","rb")

parser = argparse.ArgumentParser(description='Train or test neural net motor controller.')
parser.add_argument('--train', dest='train', action='store_true', default=False)
parser.add_argument('--test', dest='test', action='store_true', default=True)


args = parser.parse_args()


def compute_accuracy(v_xs, v_ys):
    global prediction
    y_pre = sess.run(prediction, feed_dict={xs: v_xs, keep_prob: 1, phase_train.name: True})
    
    error=tf.reduce_sum((abs(y_pre-v_ys)))

    
    result1 = sess.run(error, feed_dict={xs: v_xs, ys: v_ys, keep_prob: 1})

    return result1

def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

def conv2d(x, W):
    # stride [1, x_movement, y_movement, 1]
    # Must have strides[0] = strides[3] = 1
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
    # stride [1, x_movement, y_movement, 1]
    return tf.nn.max_pool(x, ksize=[1,2,1,1], strides=[1,2,1,1], padding='SAME')

def leakyrelu(x, alpha=0.3, max_value=None):  #alpha need set
    '''ReLU.

    alpha: slope of negative section.
    '''
    negative_part = tf.nn.relu(-x)
    x = tf.nn.relu(x)
    if max_value is not None:
        x = tf.clip_by_value(x, tf.cast(0., dtype=tf.float32),
                             tf.cast(max_value, dtype=tf.float32))
    x -= tf.constant(alpha, dtype=tf.float32) * negative_part
    return x

def full_batch_norm(x, n_out, phase_train, scope='bn'):
    """
    Batch normalization on convolutional maps.
    Args:
        x:           Tensor, 4D BHWD input maps
        n_out:       integer, depth of input maps
        phase_train: boolean tf.Varialbe, true indicates training phase
        scope:       string, variable scope
    Return:
        normed:      batch-normalized maps
    """
    with tf.variable_scope(scope):
        beta = tf.Variable(tf.constant(0.0, shape=[n_out]),
                                     name='beta', trainable=True)
        gamma = tf.Variable(tf.constant(1.0, shape=[n_out]),
                                      name='gamma', trainable=True)
        batch_mean, batch_var = tf.nn.moments(x, [0], name='moments')
        ema = tf.train.ExponentialMovingAverage(decay=0.5)

        def mean_var_with_update():
            ema_apply_op = ema.apply([batch_mean, batch_var])
            with tf.control_dependencies([ema_apply_op]):
                return tf.identity(batch_mean), tf.identity(batch_var)

        mean, var = tf.cond(phase_train,
                            mean_var_with_update,
                            lambda: (ema.average(batch_mean), ema.average(batch_var)))
        normed = tf.nn.batch_normalization(x, mean, var, beta, gamma, 1e-3)
    return normed



num_input=10
num_output=3
xs = tf.placeholder(tf.float32, [None, num_input])   
ys = tf.placeholder(tf.float32, [None, num_output])  
keep_prob = tf.placeholder(tf.float32)
lr = tf.placeholder(tf.float32)
phase_train = tf.placeholder(tf.bool, name='phase_train')


'''two layer version'''
W_fc1 = weight_variable([num_input, 500])
b_fc1 = bias_variable([500])
W_fc2 = weight_variable([500, 500])
b_fc2 = bias_variable([500])
W_fc3 = weight_variable([500, num_output])
b_fc3 = bias_variable([num_output])


h_fc1 = tf.nn.tanh(full_batch_norm(tf.matmul(tf.reshape(xs,[-1,num_input]), W_fc1) + b_fc1, 500, phase_train))
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
h_fc2 = tf.nn.tanh(full_batch_norm(tf.matmul(h_fc1_drop , W_fc2) + b_fc2, 500, phase_train))
h_fc2_drop = tf.nn.dropout(h_fc2, keep_prob)
prediction = (tf.matmul(h_fc2_drop, W_fc3) + b_fc3)

'''4 layer version'''
# W_fc1 = weight_variable([num_input, 512])
# b_fc1 = bias_variable([512])
# W_fc2 = weight_variable([512, 512])
# b_fc2 = bias_variable([512])
# W_fc3 = weight_variable([512, 128])
# b_fc3 = bias_variable([128])
# W_fc4 = weight_variable([128, 64])
# b_fc4 = bias_variable([64])
# W_fc5 = weight_variable([64, num_output])
# b_fc5 = bias_variable([num_output])

saver = tf.train.Saver()  #define saver of the check point

'''BN version'''
# h_fc1 = leakyrelu(full_batch_norm(tf.matmul(tf.reshape(xs,[-1,num_input]), W_fc1) + b_fc1, 512, phase_train))
# h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
# h_fc2 = leakyrelu(full_batch_norm(tf.matmul(h_fc1_drop , W_fc2) + b_fc2, 512, phase_train))
# h_fc2_drop = tf.nn.dropout(h_fc2, keep_prob)
# # prediction = (tf.matmul(h_fc2_drop, W_fc3) + b_fc3)

# h_fc3 = leakyrelu(full_batch_norm(tf.matmul(h_fc2_drop , W_fc3) + b_fc3, 1280, phase_train))
# h_fc3_drop = tf.nn.dropout(h_fc3, keep_prob)
# h_fc4 = leakyrelu(full_batch_norm(tf.matmul(h_fc3_drop , W_fc4) + b_fc4, 640, phase_train))
# h_fc4_drop = tf.nn.dropout(h_fc4, keep_prob)
# prediction = (tf.matmul(h_fc4_drop, W_fc5) + b_fc5)

'''no BN version'''
# h_fc1 = tf.nn.tanh(tf.matmul(tf.reshape(xs,[-1,num_input]), W_fc1) + b_fc1)
# h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
# h_fc2 = tf.nn.tanh(tf.matmul(h_fc1_drop , W_fc2) + b_fc2 )
# h_fc2_drop = tf.nn.dropout(h_fc2, keep_prob)

# h_fc3 = tf.nn.tanh((tf.matmul(h_fc2_drop , W_fc3) + b_fc3))
# h_fc3_drop = tf.nn.dropout(h_fc3, keep_prob)
# h_fc4 = tf.nn.tanh((tf.matmul(h_fc3_drop , W_fc4) + b_fc4))
# h_fc4_drop = tf.nn.dropout(h_fc4, keep_prob)
# prediction = (tf.matmul(h_fc4_drop, W_fc5) + b_fc5)

# loss = tf.reduce_mean(tf.reduce_sum(np.square(ys - prediction),
#                                         reduction_indices=[1])) 
loss=tf.losses.mean_squared_error(ys, prediction)
train_step = tf.train.AdamOptimizer(lr).minimize(loss)
sess = tf.Session()
# important step
# tf.initialize_all_variables() no long valid from
# 2017-03-02 if using tensorflow >= 0.12
if int((tf.__version__).split('.')[1]) < 12 and int((tf.__version__).split('.')[0]) < 1:
    init = tf.initialize_all_variables()
else:
    init = tf.global_variables_initializer()
sess.run(init)






loss_set=[]
step_set=[]
num_bat=1  # stack the batch to get larger training batch
if args.train:
    for i in range(1500):
        state_set=[]
        action_set=[]
        for k in range(num_bat):
            train_set=np.array(pickle.load(data_file ))
            # try:
            #     train_set=np.array(pickle.load(data_file ))
            # except:
            #     print('No more data!')
            [row,col]=train_set.shape   #(100,2)
            
            for j in range (row):
                state_set.append(train_set[j][0])
                action_set.append(train_set[j][1])
            # print(train_set[j][1])

        if i <500:
            pre,_, train_loss=sess.run([prediction,train_step,loss], feed_dict={xs: state_set, ys:action_set, \
            keep_prob: 0.9, lr:1e-1, phase_train.name: True})
        elif i< 700:
            pre,_, train_loss=sess.run([prediction,train_step,loss], feed_dict={xs: state_set, ys:action_set, \
            keep_prob: 0.9, lr:1e-2, phase_train.name: True})
        else:
            pre,_, train_loss=sess.run([prediction,train_step,loss], feed_dict={xs: state_set, ys:action_set, \
            keep_prob: 0.9, lr:1e-3, phase_train.name: True})


        print(i, train_loss)
        # print(pre)
        loss_set.append(train_loss)
        step_set.append(i)
    
    plt.plot(step_set,loss_set)
    saver.save(sess, save_file)
    plt.ylim(0,0.2)
    plt.savefig('train_curve.png')
    plt.show()


if args.test:


    screen_size = 1000  # The size of the rendered screen in pixels
    link_lengths = [0.2, 0.15, 0.1]  # These lengths are in world space (0 to 1), not screen space (0 to 1000)
    # target_pose = [0.7, 0.7]
    range_pose=0.35
    joint_angles = [0.1, 0.1, 0.1]
    link_lengths=np.array(link_lengths)*screen_size
    # target_pose=np.array(target_pose)*screen_size
    target_pose=np.random.rand(2)*2*range_pose-range_pose
    target_screen = [int((0.5 + target_pose[0]) * screen_size), int((0.5 - target_pose[1]) * screen_size)]
    reacher=Reacher(screen_size, link_lengths, joint_angles, target_screen)
    num_test_steps=15

    ini_action=[0.,90.,0.]  
    pose=reacher.step(ini_action)
    saver.restore(sess, save_file)

    for i in range (num_test_steps):
        
        state=np.concatenate((pose, target_screen))
        print(state)

        action=sess.run(prediction, feed_dict={xs: [state], keep_prob: 1, lr:0.00001, phase_train.name: False})
        # action=np.array([[0.2,0.2,0.2]])
        pose=reacher.step(screen_size*action[0])
        print('jo: ', reacher.joint_angles)
        time.sleep(0.2)
        print(i,action[0])

    index_set=[i for i in range (num_test_steps)]

   
