import os

savedir = os.environ.get('L3_A_SAVEDIR')

def make_outfile_name(infile):
    infile  = infile.replace('=', '').replace('\\', '')
    if 'nancy001' in infile:
        outdir    = '%s/nancy/i3/' % savedir
        nutype    = infile.split('/')[9]
        eregime   = infile.split('/')[10].replace('_', '')
        syst_desc = '-'.join(infile.split('/')[11:13]).replace('_', '').replace('p1','').replace('p2','').replace('.', '')
        fnum      = infile.split('/')[-1].strip('l2_')
        outfile   ='%s/JLevel_%s_%s_%s_%s' % (outdir, nutype,eregime, syst_desc, fnum)
    elif 'data/nancy/i3/' in infile:
        outdir    = '%s/nancy/h5/' % savedir
        fname   = infile.split('/')[-1].replace('i3.zst', 'h5')
        outfile = '%s/%s' % (outdir, fname)
    elif 'CORSIKA' in infile:
        outdir    = '%s/corsika/i3/' % savedir
        fname  = infile.split('/')[-1].replace('bz2', 'zst')
        outfile = '%s/%s' % (outdir, fname)
    elif 'corsika' in infile:
        outdir    = '%s/corsika/h5/' % savedir
        fname  = infile.split('/')[-1].replace('i3.zst', 'h5')
        outfile = '%s/%s' % (outdir, fname)
    elif 'GENIE' in infile:
        outdir    = '%s/genie/i3/' % savedir
        fname  = infile.split('/')[-1]
        outfile = '%s/%s' % (outdir, fname)
    elif 'genie' in infile:
        outdir    = '%s/genie/h5/' % savedir
        fname  = infile.split('/')[-1].replace('i3.zst', 'h5')
        outfile = '%s/%s' % (outdir, fname)
    elif 'exp' in infile:
        outdir    = '%s/exp_data/i3/' % savedir
        fname  = infile.split('/')[-1]
        outfile = '%s/%s' % (outdir, fname)
    else:
        quit()
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    return outfile
