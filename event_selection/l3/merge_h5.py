from glob import glob
import h5py as h5
import numpy as np

def make_new_outfile(path, keys, n_max):
     h5_write_file = h5.File(path, "w")
     for k in keys:
         h5_write_file.create_dataset(k, shape=(n_max,), dtype=np.float64)
     return h5_write_file

n_max = 1000000
path_to_files = "/data/user/jlazar/solar/solar_atmospherics/event_selection/l3/output/h5/nancy/"
fs = glob(f"{path_to_files}/Level*.h5")
print(len(fs))
for f in fs:
    h5f = h5.File(f, "r")
    keys = h5f.keys()
    if len(keys) > 1:
        break
keys = list(keys)
keys.remove('__I3Index__')
print(keys)
file_counter = 0
h5_write_file = make_new_outfile(
    f"{path_to_files}/combined_{file_counter}.h5",
    keys,
    n_max
)
data_counter = 0
for f in fs:
    h5f = h5.File(f, "r")
    if len(h5f.keys())==1:
        pass
    elif data_counter + len(h5f["ZTravel"]) > n_max:
        slc1 = slice(0, n_max - data_counter)
        slc2 = slice(n_max - data_counter, len(h5f["ZTravel"]))
        for k in keys:
            h5_write_file[k][data_counter:n_max] = h5f[k][slc1]["value"]
        file_counter += 1
        h5_write_file.close()
        print(f"{path_to_files}/combined_{file_counter}.h5")
        h5_write_file = make_new_outfile(
            f"{path_to_files}/combined_{file_counter}.h5",
            keys,
            n_max
        )
        for k in keys:
            h5_write_file[k][0:slc2.stop-slc2.start] = h5f[k][slc2]["value"]
        data_counter = slc2.stop-slc2.start
    else:
        for k in keys:
            data = h5f[k]
            h5_write_file[k][data_counter:data_counter+data.shape[0]] = data[:]["value"]
        data_counter += data.shape[0]
