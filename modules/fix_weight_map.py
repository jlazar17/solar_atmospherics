from I3Tray import NaN
def fix_weight_map(frame):
        if(not frame.Has("CorsikaWeightMap")):
                return
        cwm=frame["CorsikaWeightMap"]
        expectedKeys=["AreaSum","Atmosphere","CylinderLength","CylinderRadius","DiplopiaWeight",
        "EnergyPrimaryMax","EnergyPrimaryMin","FluxSum","FluxSum0","Multiplicity","NEvents",
        "ParticleType","PrimarySpectralIndex","SpectralIndexChange","SpectrumType","TimeScale","Weight"]

        replace=False
        nwm=cwm
        for expectedKey in expectedKeys:
                if not expectedKey in cwm.keys():
                        replace=True
                        nwm[expectedKey]=NaN
        if(replace):
                frame.Delete("CorsikaWeightMap")
                frame["CorsikaWeightMap"]=nwm
