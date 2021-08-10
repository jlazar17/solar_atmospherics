def check_same_len(mc_data):
    lst = [len(t[0]) for t in mc_data]
    return len(set(lst))==1

def mc_fname(path):
    return '.'.join(path.split('/')[-1].split('.')[:-1])

def mc_name(path):
    path = path.lower()
    #TODO figure out a better way to do this
    if 'hmniederhausen/' in path:
        name = 'intracks'
    elif 'northern_tracks' in path:
        name = 'ntracks'
    elif ('oscnext' in path):
        if 'genie' in path:
            name = 'oscNext'
        elif 'muongun' in path:
            name = 'oscNext_muon'
    elif 'big_files' in path:
        if 'nancy' in path:
            name = 'nancy'
        elif 'genie' in path:
            name = 'genie'
        elif 'corsika' in path:
            name = 'corsika'
    else:
        raise RuntimeError('Event selection not recognized')
    return name
