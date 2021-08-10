import numpy as np
import tables
#from solar_atmospherics import outdescs_dict
#l3_b_keys = [tup[0] for tup in outdescs_dict['l3_b']]


def make_slices(n_items, chunk_size=1e4, thin=1):
    chunk_slices = []
    n0 = 0
    n1 = 0
    while n1<n_items:
        n1 = min(n1+int(chunk_size*thin), n_items)
        chunk_slices.append(slice(n0, n1, thin))
        n0 = n1
    return chunk_slices

def read_file_in_chunks(fname, outkeys, chunk_size=1e4, thin=1):
#def read_file_in_chunks(fname, chunk_size=1e4, thin=1, outkeys=l3_b_keys):
    f            = tables.File(fname)
    n_items      = f.root.BayesRatio.shape[0]
    chunk_slices = make_slices(n_items, chunk_size=chunk_size, thin=thin)
    n_entries    = np.ceil(n_items/thin)
    dtypes       = [(key, '<f8') for key in outkeys]
    vals         = np.zeros((int(n_entries), len(outkeys)))
    for slc in chunk_slices:
        n0 = int(slc.start/slc.step)
        if slc.stop==n_items:
            n1 = None
        else:
            n1 = int(slc.stop/slc.step)
        for i,key in enumerate(outkeys):
            vals[n0:n1,i] = getattr(f.root, key)[slc]
    vals = [tuple(_) for _ in vals]
    arr = np.array(vals, dtype=dtypes)
    return arr
