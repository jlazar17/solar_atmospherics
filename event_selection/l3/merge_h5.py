from glob import glob
import h5py as h5
import numpy as np

def initialize_parser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--indir",
        dest="indir",
        type = str,
        required=True
    )
    parser.add_argument(
        "-o",
        "--outdir",
        dest = "outdir",
        type = str,
        default = ""
    )
    parser.add_argument(
        "--prefix"
        dest = "prefix",
        default = "",
        type = str,
    )
    parser.add_argument(
        "-n",
        "--nmax",
        dest = nmax,
        default = 1000000,
        type = int
    )
    args = parser.parse_args()
    return args

def make_new_outfile(path, keys, nmax):
     h5_write_file = h5.File(path, "w")
     for k in keys:
         h5_write_file.create_dataset(k, shape=(nmax,), dtype=np.float64)
     return h5_write_file

def main(indir, outdir, prefix, nmax, track_progress=False):
    fs = glob(f"{indir}/Level*.h5")
    if track_progress:
        from tqdm import tqdm
        itr = tqdm(fs)
    else:
        itr = fs``
    for f in itr:
        h5f = h5.File(f, "r")
        keys = h5f.keys()
        if len(keys) > 1:
            break
    keys = list(keys)
    keys.remove('__I3Index__')
    file_counter = 0
    h5_write_file = make_new_outfile(
        f"{outdir}/{prefix}combined_{file_counter}.h5",
        keys,
        nmax
    )
    data_counter = 0
    for f in fs:
        h5f = h5.File(f, "r")
        if len(h5f.keys())==1:
            pass
        elif data_counter + len(h5f["ZTravel"]) > nmax:
            slc1 = slice(0, nmax - data_counter)
            slc2 = slice(nmax - data_counter, len(h5f["ZTravel"]))
            for k in keys:
                h5_write_file[k][data_counter:nmax] = h5f[k][slc1]["value"]
            file_counter += 1
            h5_write_file.close()
            h5_write_file = make_new_outfile(
                f"{outdir}/combined_{file_counter}.h5",
                keys,
                nmax
            )
            for k in keys:
                h5_write_file[k][0:slc2.stop-slc2.start] = h5f[k][slc2]["value"]
            data_counter = slc2.stop-slc2.start
        else:
            for k in keys:
                data = h5f[k]
                h5_write_file[k][data_counter:data_counter+data.shape[0]] = data[:]["value"]
            data_counter += data.shape[0]
if __name__=="__main__":

    args = initialize_parser()

    indir = args.indir
    outdir = args.outdir
    prefix = args.prefix
    nmax = args.nmax
    
    main(indir, outdir, prefix, nmax)
