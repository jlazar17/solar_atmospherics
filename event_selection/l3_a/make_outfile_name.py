def make_outfile_name(infile, outdir="."):
    infile  = infile.replace('=', '').replace('\\', '')
    if 'nancy001' in infile:
        nutype    = infile.split('/')[9]
        eregime   = infile.split('/')[10].replace('_', '')
        syst_desc = '-'.join(infile.split('/')[11:13]).replace('_', '').replace('p1','').replace('p2','').replace('.', '')
        fnum      = infile.split('/')[-1].strip('l2_')
        outfile   ='%s/JLevel_%s_%s_%s_%s' % (outdir, nutype,eregime, syst_desc, fnum)
    elif 'data/nancy/i3/' in infile:
        fname   = infile.split('/')[-1].replace('i3.zst', 'h5')
        outfile = '%s/%s' % (outdir, fname)
    elif 'CORSIKA' in infile:
        fname  = infile.split('/')[-1].replace('bz2', 'zst')
        outfile = '%s/%s' % (outdir, fname)
    elif 'corsika' in infile:
        fname  = infile.split('/')[-1].replace('i3.zst', 'h5')
        outfile = '%s/%s' % (outdir, fname)
    elif 'GENIE' in infile:
        fname  = infile.split('/')[-1]
        outfile = '%s/%s' % (outdir, fname)
    elif 'genie' in infile:
        fname  = infile.split('/')[-1].replace('i3.zst', 'h5')
        outfile = '%s/%s' % (outdir, fname)
    elif 'exp' in infile:
        fname  = infile.split('/')[-1]
        outfile = '%s/%s' % (outdir, fname)
    else:
        raise ValueError(f"Cannot determine outdir from infile: {infile}")
    return outfile
