import os
import numpy as np
import h5py as h5
from typing import Iterable, Optional, Union
from datetime import datetime

from solar_common import sun, compute_average_distribution
from solar_common.flux import EventFlux, SkyDistribution
from solar_common.event_reader import EventReader, Selection, DataType

MJDMIN = 56_293 # Jan. 1 2013
MJDMAX = 56_658.25 # Jan. 1 2014 + 0.25 days for stuff

def determine_selection(datafile: str) -> Selection:
    # This is jank but I don't have an alternative at present :-)
    # Only the point source uses numpy files
    if datafile.endswith(".npy"):
        return Selection.POINTSOURCE
    # oscNext uses h5 files as labels them verbosely
    elif datafile.endswith(".hdf5"):
        return Selection.OSCNEXT

def get_event_flux(fluxfile: str, key: str) -> EventFlux:
    """Makes EventFlux object input h5 file name where fluxes are stored
    and a given key

    params
    ______
    fluxfile: h5file where fluxes are stored
    key: Name of the field in h5 file where flux and metadata are stored

    returns
    _______
    event_flux: EventFlux object
    """
    with h5.File(fluxfile) as h5f:
        event_flux = EventFlux(
            h5f[key][:],
            getattr(SkyDistribution, h5f[key].attrs["Distribution"])
        )
    return event_flux

def save_output(
    outfile: str,
    key_prefix: str,
    average_dist: np.ndarray,
    **kwargs
) -> None:
    """Saves output to file at input string. Adds any metadata which may be supplied
    as a kwarg

    params
    ______
    outfile: h5 file to save information to
    key_prefix: where to save the dataset in the file. Integers will be added 
        to make it a unique key each time
    average_dist: average distribution
    kwargs: key, value pairs to add to the `attrs` of the dataset
    """

    with h5.File(outfile, "r+") as h5f:
        idx = 0
        key = f"{key_prefix}_{idx}"
        while key in h5f.keys():
            idx += 1
            key = f"{key_prefix}_{idx}"
        h5f.create_dataset(key, data=average_dist)
        for k, v in kwargs.items():
            h5f[key].attrs[k] = v

def main(
    fluxfile: str,
    eventsfile: str,
    outfile: str,
    seed: int,
    keys: Optional[Union[None, Iterable[str]]] = None,
    mjdmin: Optional[float] = MJDMIN,
    mjdmax: Optional[float] = MJDMAX,
    ndays: Optional[int] = 1_000,
) -> None:
    """Computes the analysis level distributions in \Delta\psi, E_{reco},
    and potentially other variables averaged over an input number
    of days. These days are sampled uniformly from a range which can 
    be optionally specified

    params
    ______
    fluxfile: h5file where fluxes are stored
    eventsfile: file where the events to be used are stored
    outfile: h5 file where we should save the output
    keys: keys from h5file to generate distributions for. If `None`, distributions will be
        generated for all keys
    seed: random number generation seed
    mjdmin: minimum modified Julian date for uiform sampling range
    mjdmax: maximum modified Julian date for uiform sampling range
    """
    # Get the keys from the outfile if not provided
    if keys is None or len(keys)==0:
        with h5.File(fluxfile, "r") as h5f:
            keys = list(h5f.keys())

    # Make the output file if it doesn't exist
    if not os.path.exists(outfile):
        with h5.File(outfile) as _:
            pass

    selection = determine_selection(eventsfile)
    # MAKE THIS ACCEPT NON-MC STUFF
    events = EventReader(eventsfile, selection, DataType.MC)

    # Set the RNG seed
    for key in keys:
        flux = get_event_flux(fluxfile, key)
        np.random.seed(seed)
        mjds = np.random.uniform(mjdmin, mjdmax, ndays)
        avg = compute_average_distribution(events, sun, flux, mjds)
        save_output(
            outfile,
            key, 
            avg,
            ndays=ndays,
            mjdmin=mjdmin,
            mjdmax=mjdmax,
            seed=seed,
            dtstr=datetime.now().strftime("%B %d, %Y"),
            eventsfile=eventsfile
        )
        seed += 1

if __name__=="__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        "--fluxfile",
        required=True
    )
    parser.add_argument(
        "--eventsfile",
        required=True
    )
    parser.add_argument(
        "--outfile",
        required=True
    )
    parser.add_argument(
        "--seed",
        "-s",
        dest="seed",
        type=int
    )
    parser.add_argument(
        "--keys",
        nargs="+"
    )
    parser.add_argument(
        "--mjdmin",
        default=MJDMIN
    )
    parser.add_argument(
        "--mjdmax",
        default=MJDMAX
    )
    parser.add_argument(
        "-n",
        "--ndays",
        dest="ndays",
        default=1000,
        type=int
    )
    args = parser.parse_args()
    main(
        args.fluxfile,
        args.eventsfile,
        args.outfile,
        args.seed,
        keys=args.keys,
        mjdmin=args.mjdmin,
        mjdmax=args.mjdmax,
        ndays=args.ndays
    )
