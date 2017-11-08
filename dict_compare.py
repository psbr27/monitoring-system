#!/usr/bin/env python
def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    return added, removed, modified, same

#x = dict(a=1, b=2)
#y = dict(a=2, b=2)
#added, removed, modified, same = dict_compare(x, y)
#print(added)
#print(removed)
#print(modified)
##print(same)
