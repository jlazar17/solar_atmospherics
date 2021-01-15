from final_selection import finalSample
from icecube import VHESelfVeto
from is_simulation import is_simulation

def _FindDetectorVolumeIntersections(recoParticle, geometry):
    intersectionPoints = VHESelfVeto.IntersectionsWithInstrumentedVolume(geometry, recoParticle)
    intersectionTimes = []
    for intersectionPoint in intersectionPoints:
        vecX = intersectionPoint.x - recoParticle.pos.x
        vecY = intersectionPoint.y - recoParticle.pos.y
        vecZ = intersectionPoint.z - recoParticle.pos.z

        prod = vecX*recoParticle.dir.x + vecY*recoParticle.dir.y + vecZ*recoParticle.dir.z
        dist = math.sqrt(vecX**2 + vecY**2 + vecZ**2)
        if prod < 0.: dist *= -1.

        if abs(prod-dist) > 1e-3*icetray.I3Units.m:
            raise RuntimeError("intersection points are not on track")

        intersectionTimes.append(dist/dataclasses.I3Constants.c + recoParticle.time)

    sortedTimes = sorted(intersectionTimes)
    return sortedTimes

def FindDetectorVolumeIntersections(frame, TrackName="", OutputTimeWindow=None, TimePadding=0.):
    if not (finalSample & is_simulation)(frame):
        return
    if OutputTimeWindow is not None:
        twName = OutputTimeWindow
    else:
        twName = TrackName + "TimeRange"

    theTrack = frame[TrackName]
    geometry = frame["I3Geometry"]

    times = _FindDetectorVolumeIntersections(theTrack, geometry)

    if len(times) == 0:
        #raise RuntimeError("track does not intersect the detector volume")
        frame[twName] = dataclasses.I3TimeWindow()
    elif len(times) == 1:
        raise RuntimeError("tracks with only one intersection are not supported")
    else:
        tWindow = dataclasses.I3TimeWindow(times[0]-TimePadding, times[-1]+TimePadding)
        frame[twName] = tWindow

