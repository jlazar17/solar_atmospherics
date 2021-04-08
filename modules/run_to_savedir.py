from glob import glob
good_run_files = [
                  '/data/exp/IceCube/2011/filtered/level2pass2a/IC86_2011_GoodRunInfo.txt',
                  '/data/exp/IceCube/2012/filtered/level2pass2a/IC86_2012_GoodRunInfo.txt',
                  '/data/exp/IceCube/2013/filtered/level2pass2a/IC86_2013_GoodRunInfo.txt',
                  '/data/exp/IceCube/2014/filtered/level2pass2a/IC86_2014_GoodRunInfo.txt',
                  '/data/exp/IceCube/2015/filtered/level2pass2a/IC86_2015_GoodRunInfo.txt',
                  '/data/exp/IceCube/2016/filtered/level2pass2a/IC86_2016_GoodRunInfo.txt',
                  '/data/exp/IceCube/2017/filtered/level2pass2a/IC86_2017_GoodRunInfo.txt',
                  '/data/exp/IceCube/2018/filtered/level2/IC86_2018_GoodRunInfo.txt',
                  '/data/exp/IceCube/2019/filtered/level2/IC86_2019_GoodRunInfo.txt',
                  '/data/exp/IceCube/2020/filtered/level2/IC86_2020_GoodRunInfo.txt',
                 ]
run_info = {}

for grf in good_run_files:
    with open(grf) as f:
        for l in f.read().split('\n')[:-1]:
            if 'runnum' not in l.lower() and 'good' not in l.lower():
                splitline = [a for a in l.split(' ') if a!='']
                GCD = glob(splitline[7]+'*GCD*')
                if len(GCD)!=1:
                    continue
                run_info[int(splitline[0])] = (int(splitline[1]), int(splitline[2]), float(splitline[3]), splitline[7], glob(splitline[7]+'*GCD*')[0])
