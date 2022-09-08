from glob import glob
fs = glob("/data/user/jlazar/solar/solar_atmospherics/event_selection/l3_a/output/i3/corsika///*")
fs = [x.split("/")[-1] for x in fs]

unprocessed_corsika = []
with open("/data/user/jlazar/solar/solar_atmospherics/event_selection//l3_a/input/i3/corsika/input_corsika_l3_a_i3.txt", "r") as input_fs:
    for i, line in enumerate(input_fs.readlines()):
        if i % 1000==0:
            print(f"{i} out of {len(fs)}")
        split_line = line.strip("\n").split("/")
        desc = "Level3a" + split_line[-1][6:]
        if not desc in fs:
            unprocessed_corsika.append(line)
with open("/data/user/jlazar/solar/solar_atmospherics/event_selection/l3_a/input/i3/corsika/unprocessed_files.txt", "w") as outf:
    for f in unprocessed_corsika:
        outf.write(f)
