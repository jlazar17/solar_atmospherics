def fix_weight_map(frame):
    from I3Tray import NaN
    if(not frame.Has("CorsikaWeightMap")):
        return
    else:
        cwm = frame["CorsikaWeightMap"]
        expected_keys = [
            "AreaSum",
            "Atmosphere",
            "CylinderLength",
            "CylinderRadius",
            "DiplopiaWeight",
            "EnergyPrimaryMax",
            "EnergyPrimaryMin",
            "FluxSum",
            "FluxSum0",
            "Multiplicity",
            "NEvents",
            "ParticleType",
            "PrimarySpectralIndex",
            "SpectralIndexChange",
            "SpectrumType",
            "TimeScale",
            "Weight"
        ]

        replace = False
        nwm = cwm
        for key in expected_keys:
            if not key in cwm.keys():
                replace = True
                nwm[key] = NaN
        if replace:
            frame.Delete("CorsikaWeightMap")
            frame["CorsikaWeightMap"] = nwm
