from __future__ import print_function

''' 
p_datautils.py:  Just some routines that we use for moving data around
'''

import numpy as np
import librosa
import os
from os.path import isfile
from timeit import default_timer as timer


channels = 1   #  mono audio


def get_class_names(path="Preproc/"):  # class names are subdirectory names in Preproc/ directory
    class_names = os.listdir(path)
    return class_names

def get_total_files(path="Preproc/",train_percentage=0.8): 
    sum_total = 0
    sum_train = 0
    sum_test = 0
    subdirs = os.listdir(path)
    for subdir in subdirs:
        files = os.listdir(path+subdir)
        n_files = len(files)
        sum_total += n_files
        n_train = int(train_percentage*n_files)
        n_test = n_files - n_train
        sum_train += n_train
        sum_test += n_test
    return sum_total, sum_train, sum_test

def get_sample_dimensions(path='Preproc/'):
    classname = os.listdir(path)[0]
    files = os.listdir(path+classname)
    infilename = files[0]
    audio_path = path + classname + '/' + infilename
    melgram = np.load(audio_path)
    print("   get_sample_dimensions: melgram.shape = ",melgram.shape)
    return melgram.shape
 

def encode_class(class_name, class_names):  # makes a "one-hot" vector for each class name called
    try:
        idx = class_names.index(class_name)
        vec = np.zeros(len(class_names))
        vec[idx] = 1
        return vec
    except ValueError:
        return None


def decode_class(vec, class_names):  # generates a number from the one-hot vector
    return int(np.argmax(vec))

# don't need this if we just shuffle each directory listing
#def shuffle_XY_paths(X,Y,paths):   # generates a randomized order, keeping X&Y(&paths) together
#    assert (X.shape[0] == Y.shape[0] )
#    idx = np.array(range(Y.shape[0]))
#    np.random.shuffle(idx)
#    newX = np.copy(X)
#    newY = np.copy(Y)
#    newpaths = paths
#    for i in range(len(idx)):
#        newX[i] = X[idx[i],:,:]
#        newY[i] = Y[idx[i],:]
#        newpaths[i] = paths[idx[i]]
#    return newX, newY, newpaths


'''
So we make the training & testing datasets here, and we do it separately.
Why not just make one big dataset, shuffle, and then split into train & test?
because we want to make sure statistics in training & testing are as similar as possible
'''
def build_datasets(train_percentage=0.8, preproc=True):

    if (preproc):
        path = "Preproc/"
    else:
        path = "Samples/"

    class_names = get_class_names(path=path)
    print("class_names = ",class_names)

    total_files, total_train, total_test = get_total_files(path=path, train_percentage=train_percentage)
    print("total files = ",total_files)

    nb_classes = len(class_names)

    # pre-allocate memory for speed (old method used np.concatenate, slow)
    mel_dims = get_sample_dimensions(path=path)  # Find out the 'shape' of each data file
    print(" melgram dimensions: ",mel_dims)
    X_train = np.zeros((total_train, mel_dims[1], mel_dims[2], mel_dims[3]))   
    Y_train = np.zeros((total_train, nb_classes))  
    X_test = np.zeros((total_test, mel_dims[1], mel_dims[2], mel_dims[3]))  
    Y_test = np.zeros((total_test, nb_classes))  
    paths_train = []
    paths_test = []

    train_count = 0
    test_count = 0
    for idx, classname in enumerate(class_names):
        this_Y = np.array(encode_class(classname,class_names) )
        this_Y = this_Y[np.newaxis,:]
        class_files = os.listdir(path+classname)
        n_files = len(class_files)
        n_load =  n_files
        n_train = int(train_percentage * n_load)
        printevery = 100

        file_list = class_files[0:n_load]
        np.random.shuffle(file_list)   # shuffle directory listing (e.g. to avoid alphabetic order)
        for idx2, infilename in enumerate(file_list):          
            audio_path = path + classname + '/' + infilename
            if (0 == idx2 % printevery):
                print('\r Loading class: {:14s} ({:2d} of {:2d} classes)'.format(classname,idx+1,nb_classes),
                       ", file ",idx2+1," of ",n_load,": ",audio_path,sep="")
            #start = timer()
            if (preproc):
              melgram = np.load(audio_path)
              #print("melgram.shape = ",melgram.shape)
              sr = 44100
            else:
                raise(" You should preprocess first")

            if (idx2 < n_train):                   # Training dataset
                X_train[train_count,:,:] = melgram
                Y_train[train_count,:] = this_Y
                paths_train.append(audio_path)     
                train_count += 1
            else:
                X_test[test_count,:,:] = melgram    # Testing dataset
                Y_test[test_count,:] = this_Y
                paths_test.append(audio_path)
                test_count += 1
        #print("")

 #   print("Shuffling order of data...")
 #   X_train, Y_train, paths_train = shuffle_XY_paths(X_train, Y_train, paths_train)
 #   X_test, Y_test, paths_test = shuffle_XY_paths(X_test, Y_test, paths_test)

    return X_train, Y_train, paths_train, X_test, Y_test, paths_test, class_names, sr
