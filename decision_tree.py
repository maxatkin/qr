import pandas as pd
import numpy as np
import math

def entropy_(x):
    if x == 0.0:
        return 0.0
    return -x * math.log(x,2)
entropy = np.vectorize(entropy_)

def get_best_split(s, feats):
    N = len(s)
    bestH = None

    classes = s['target'].unique()
    if len(classes) == 1:
        return None
    
    for i, f in enumerate(feats):
        dfs = s.sort_values(by = f).reset_index(drop = True)
        pk = list()
        dup_mask = dfs[f].diff(-1) < 0
        if sum(dup_mask) == 0:
            continue

        for v in classes:
            cs = (dfs['target'] == v).cumsum().astype(float)
            set_size = pd.Series(dfs.index.values + 1)
            total = cs.iloc[-1]
            p = (cs[dup_mask] / set_size[dup_mask])
            q = (total - cs[dup_mask]) / (N - set_size[dup_mask])
            w = set_size[dup_mask]
            pk.append(w*entropy(p) + (N-w)*entropy(q)) 
            
        H = pd.DataFrame(np.vstack(pk).T).sum(axis = 1)
        idx = np.argmin(H)
        best = dfs.index.values[np.where(dup_mask)][idx]
        
        if bestH > H[idx] or bestH is None:
            bestH = H[idx]
            split = 0.5*(dfs[f].iloc[best] + dfs[f].iloc[best + 1]) 
            bestf = f
            besti = i
            
    return (bestf, besti, split, bestH)

class CTree(object):
    def __init__(self, max_depth = -1):
        self.left = None
        self.right = None
        self.max_depth = max_depth
        self.is_leaf = False
        
    def fit(self, X, y):
        self.feats = X.columns
        s = pd.concat([X, y], axis = 1) 
        res = get_best_split(s, self.feats)
        if res is None or self.max_depth == 0:
            self.is_leaf = True
        else:
            (self.split_feat_name, self.split_feat,
             self.split, self.split_H) = res
            mask = s[self.split_feat_name] < self.split
            self.left = CTree(max_depth = self.max_depth - 1)
            self.right = CTree(max_depth = self.max_depth - 1)
            self.left.fit(X[mask], y[mask])
            self.right.fit(X[~mask], y[~mask])

    def show(self, max_depth):
        if self.is_leaf is False:
            print (max_depth - self.max_depth)*'\t', self.split_feat_name, '<', self.split
            self.left.show(max_depth)
            self.right.show(max_depth)
        else:
            print (max_depth - self.max_depth)*'\t', "Leaf"