"""
stitch_quads.py

Stitches together four (reprojected) raw-byte quadrants

See 'usage_string' definition for usage
"""

import os
import sys
import numpy as np
from netCDF4 import Dataset

usage_string = """

    Usage:
          python stitch_quads.py <grid_name> <basename>
        eg
          python stitch_quads.py psn25 regions_20210924_nh_3411
"""


grid_info_dict = {
    'psn25': {
        'grid_name': 'psn25',
        'xleft': 154,
        'xright': 150,
        'yupper': 234,
        'ylower': 214, },
    'psn12.5': {
        'grid_name': 'psn12.5',
        'xleft': 308,
        'xright': 300,
        'yupper': 468,
        'ylower': 428, },
    'psn6.25': {
        'grid_name': 'psn6.25',
        'xleft': 616,
        'xright': 600,
        'yupper': 936,
        'ylower': 856, },
    'psn3.125': {
        'grid_name': 'psn3.125',
        'xleft': 1232,
        'xright': 1200,
        'yupper': 1872,
        'ylower': 1712, },
    'pss25': {
        'grid_name': 'pss25',
        'xleft': 158,
        'xright': 158,
        'yupper': 174,
        'ylower': 158, },
    'pss12.5': {
        'grid_name': 'pss12.5',
        'xleft': 316,
        'xright': 316,
        'yupper': 348,
        'ylower': 316, },
    'pss6.25': {
        'grid_name': 'pss6.25',
        'xleft': 632,
        'xright': 632,
        'yupper': 696,
        'ylower': 632, },
    'pss3.125': {
        'grid_name': 'pss3.125',
        'xleft': 1264,
        'xright': 1264,
        'yupper': 1392,
        'ylower': 1264, },
    'e2n25': {
        'grid_name': 'e2n25',
        'xleft': 360,
        'xright': 360,
        'yupper': 360,
        'ylower': 360, },
    'e2n12.5': {
        'grid_name': 'e2n12.5',
        'xleft': 720,
        'xright': 720,
        'yupper': 720,
        'ylower': 720, },
    'e2n6.25': {
        'grid_name': 'e2n6.25',
        'xleft': 1440,
        'xright': 1440,
        'yupper': 1440,
        'ylower': 1440, },
    'e2n3.125': {
        'grid_name': 'e2n3.125',
        'xleft': 2880,
        'xright': 2880,
        'yupper': 2880,
        'ylower': 2880, },
    'e2s25': {
        'grid_name': 'e2s25',
        'xleft': 360,
        'xright': 360,
        'yupper': 360,
        'ylower': 360, },
    'e2s12.5': {
        'grid_name': 'e2s12.5',
        'xleft': 720,
        'xright': 720,
        'yupper': 720,
        'ylower': 720, },
    'e2s6.25': {
        'grid_name': 'e2s6.25',
        'xleft': 1440,
        'xright': 1440,
        'yupper': 1440,
        'ylower': 1440, },
    'e2s3.125': {
        'grid_name': 'e2s3.125',
        'xleft': 2880,
        'xright': 2880,
        'yupper': 2880,
        'ylower': 2880, },
}


def xwm(m='exiting in xwm()'):
    raise SystemExit(m)


def stitch_quads(bfn, grid_info, n_regions, overwrite=True):
    # ofn = bfn + '.nc'
    # ofn = bfn + '.dat'
    # ofn = bfn + f'_{grid_info["grid_name"]}' + '.dat'
    ofn = bfn + '.dat'
    if not overwrite and os.path.exists(ofn):
        xwm(f'{ofn} exists, but overwrite is False')

    xleft = grid_info['xleft']
    xright = grid_info['xright']
    yupper = grid_info['yupper']
    ylower = grid_info['ylower']
    try:
        varname = grid_info['varname']
    except KeyError:
        varname = 'Band1'

    quad_list = ('UL', 'UR', 'LR', 'LL')
    # quad_dim_pairs are xdim, ydim indexes
    quad_dim_pairs = {
        'UL': ('xleft', 'yupper'),
        'UR': ('xright', 'yupper'),
        'LR': ('xright', 'ylower'),
        'LL': ('xleft', 'ylower')}
    quad_data = {}
    for quad in quad_list:
        quad_fn = f'{bfn}_{quad}.nc'

        xdim = grid_info[quad_dim_pairs[quad][0]]
        ydim = grid_info[quad_dim_pairs[quad][1]]

        print(f'{quad}: ({xdim}, {ydim})')

        quad_data[quad] = np.zeros((ydim, xdim), dtype=np.uint8)

        qds = Dataset(quad_fn, 'r')
        qds.set_auto_maskandscale(False)
        nc_quad_data = qds.variables[varname]
        nc_quad_data_shape = nc_quad_data.shape
        assert nc_quad_data_shape == (ydim, xdim)

        # tempdata = np.array(nc_quad_data).astype(np.uint8)
        # tempdata.tofile(f'temp_{quad}.dat')

        quad_data[quad][:] = qds.variables[varname][:]
        # By default, the data from the netCDF quadrant files are upside down
        quad_data[quad] = np.flipud(quad_data[quad])
        # Limit to number of regions
        quad_data[quad][quad_data[quad] > n_regions] = 0

    full_xdim = xleft + xright
    full_ydim = ylower + yupper
    data = np.zeros((full_ydim, full_xdim), dtype=np.uint8)

    # When writing these, recall that upper left corner is zero (min-x, max-y)
    data[:yupper, :xleft] = quad_data['UL']
    data[:yupper, xleft:] = quad_data['UR']
    data[yupper:, xleft:] = quad_data['LR']
    data[yupper:, :xleft] = quad_data['LL']

    data.tofile(ofn)
    print(f'  Wrote data to: {ofn}')
    print(f'    of shape: ({full_xdim}, {full_ydim})')


def determine_num_regions(bfn, grid_name):
    # Attempt to determine the number of regions by querying the base .csv file
    if 'psn' in grid_name or 'e2n' in grid_name:
        return 18
    if 'pss' in grid_name or 'e2s' in grid_name:
        return 5
    else:
        xwm(f'Unknown number of regions for grid: {grid_name}')

    """ 
    # The "right" way to do this is to figure out the .csv file and
    # determine which region numbers are used.
    import glob
    csv_fn_list = sorted(glob.glob('*.csv'))
    print(f'bfn: {bfn}')
    print(f'grid_name: {grid_name}')
    for csv_fn in csv_fn_list:
        print(f'csv file: {csv_fn}')
    ...
    """


if __name__ == '__main__':
    try:
        bfn = sys.argv[1]
    except IndexError:
        print('\nNo base filename provided')
        xwm(f'{usage_string}')

    try:
        grid_name = sys.argv[2]
        grid_info = grid_info_dict[grid_name]
    except IndexError:
        print('\nNo grid name provided')
        xwm(f'{usage_string}')
    except KeyError:
        print(f'\nNo such grid_name defined: {grid_name}\n')
        xwm(f'Possible grid names: {" ".join(key for key in grid_info_dict.keys())}')  #noqa

    n_regions = determine_num_regions(bfn, grid_name)
    print(f'n_regions: {n_regions}')
    stitch_quads(bfn, grid_info, n_regions)
