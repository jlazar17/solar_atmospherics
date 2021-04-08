import os
def make_outfile_name(infile):
    infile  = infile.replace('=', '').replace('\\', '')
    outfile = infile.replace('l3_a', 'l3_b')
    outdir  = '/'.join(outfile.split('/')[:-1])
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    return outfile
