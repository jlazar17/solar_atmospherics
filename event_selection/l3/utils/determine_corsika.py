def determine_corsika(infile):
    s = infile.split("/")[-1]
    s = int(s.split(".")[-4])
    return s
