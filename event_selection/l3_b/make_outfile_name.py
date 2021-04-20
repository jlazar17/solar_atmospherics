import os
def make_outfile_name(infile):
    outdir  = os.enviro.get('L3_B_SAVEDIR')
    infile  = infile.replace('=', '').replace('\\', '')
    fname   = infile.split('/')[-1].replace('l3_a', 'l3_b')
    outfile = '%s/%s' % (outdir, fname)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    return outfile
