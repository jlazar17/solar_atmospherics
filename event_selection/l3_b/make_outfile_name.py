import os
def make_outfile_name(infile):
    infile  = infile.replace('=', '').replace('\\', '')
    print(infile)
    outfile = infile.replace('l3_a', 'l3_b')
    outdir  = '/'.join(outfile.split('/')[:-1])
    #if 'nancy001' in infile:
    #    outdir    = '/data/user/jvillarreal/solar_atmospherics/event_selection/l3_a/data/nancy/i3/'
    #    nutype    = infile.split('/')[9]
    #    eregime   = infile.split('/')[10].replace('_', '')
    #    syst_desc = '-'.join(infile.split('/')[11:13]).replace('_', '').replace('p1','').replace('p2','').replace('.', '')
    #    fnum      = infile.split('/')[-1].strip('l2_')
    #    outfile   ='%s/JLevel_%s_%s_%s_%s' % (outdir, nutype,eregime, syst_desc, fnum)
    #elif 'data/nancy/i3/' in infile:
    #    outdir    = '/data/user/jvillarreal/solar_atmospherics/event_selection/l3_a/data/nancy/h5/'
    #    fname   = infile.split('/')[-1].replace('i3.zst', 'h5')
    #    outfile = '%s/%s' % (outdir, fname)
    #elif 'CORSIKA' in infile:
    #    outdir    = '/data/user/jvillarreal/solar_atmospherics/event_selection/l3_a/data/corsika/i3/'
    #    fname  = infile.split('/')[-1].replace('bz2', 'zst')
    #    outfile = '%s/%s' % (outdir, fname)
    #elif 'corsika' in infile:
    #    outdir    = '/data/user/jvillarreal/solar_atmospherics/event_selection/l3_a/data/corsika/h5/'
    #    fname  = infile.split('/')[-1].replace('i3.zst', 'h5')
    #    outfile = '%s/%s' % (outdir, fname)
    #elif 'GENIE' in infile:
    #    outdir    = '/data/user/jvillarreal/solar_atmospherics/event_selection/l3_a/data/genie/i3/'
    #    fname  = infile.split('/')[-1]
    #    outfile = '%s/%s' % (outdir, fname)
    #elif 'genie' in infile:
    #    outdir    = '/data/user/jvillarreal/solar_atmospherics/event_selection/l3_a/data/genie/h5/'
    #    fname  = infile.split('/')[-1].replace('i3.zst', 'h5')
    #    outfile = '%s/%s' % (outdir, fname)
    #elif 'exp' in infile:
    #    print(1)
    #    outdir    = '/data/user/jvillarreal/solar_atmospherics/event_selection/l3_a/data/exp_data/i3/'
    #    fname  = infile.split('/')[-1]
    #    outfile = '%s/%s' % (outdir, fname)
    #else:
    #    quit()
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    return outfile
