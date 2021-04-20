import os
def make_outfile_name(infile):
    infile  = infile.replace('=', '').replace('\\', '')
    fname   = infile.split('/')[-1].replace('l3_a', 'l3_b')
    outdir  = '%s/%s/%s/' % (os.environ.get('L3_B_SAVEDIR'), infile.split('/')[-3], infile.split('/')[-2])
    outfile = outdir + fname
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    return outfile
