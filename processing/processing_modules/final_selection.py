from splitFrames import splitFrames
from afterpulses import afterpulses
from goodFit import goodFit
from cutL3 import cutL3
finalSample = splitFrames & ~afterpulses & goodFit
#finalSample = splitFrames & ~cutL3 & ~afterpulses & goodFit

