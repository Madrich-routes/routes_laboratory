import pickle
import numpy as np
with open('res_matrix.pkl', 'rb') as f:
    matr = pickle.load(f)


print((np.where(matr[0] == None)))
