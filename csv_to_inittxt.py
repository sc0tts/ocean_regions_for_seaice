"""
csv_to_inittxt.py

Convert Walt's xls-derived .csv file to suitable .txt file

Usage:
    python csv_to_inittxt.py Regsions_apr20.csv regions_apr20.txt
"""

import sys
import pandas as pd


def xwm(m='exiting in xwm()'):
    raise SystemExit(m)


def csv_to_txt(ifn, ofn):
    """Convert QGIS WKT-CSV output to text file"""
    print(' ')
    print(f'Input:  {ifn}')
    print(f'Output: {ofn}')
    print(' ')

    # Print everything in the dataset
    pd.set_option('display.max_rows', None)

    df = pd.read_csv(ifn)
    print(f'Input\n\n{df.head()}')

    df2 = df[['Region', 'Lat', 'Lon', 'RegionNo', 'VertexNo']]

    # Print unique values of a column
    # print(f'{df2["RegionNo"].unique()}')

    # Convert some columns to integer
    df2['RegionNo'] = df2['RegionNo'].astype(int)
    df2['VertexNo'] = df2['VertexNo'].astype(int)

    # Remove spaces from region names
    df2['Region'] = df2['Region'].str.replace(' ', '_')
    print(f'{df2.head()}')
    print(f'Unique Regions: {df2["Region"].unique()}')

    # Rename columns
    print(df2.columns)
    df2.rename(columns={
        'Region': 'Name',
        'Lat': 'Latitude',
        'Lon': 'Longitude',
        'RegionNo': 'Sea_ID',
        'VertexNo': 'Vertex_Index',
    }, inplace=True)
    print(df2.columns)

    df2.to_csv(
        ofn,
        sep=' ',
        float_format='%.4f',
        index=False,
    )


if __name__ == '__main__':
    try:
        ifn = sys.argv[1]
    except IndexError:
        xwm('First argument is input filename (csv)')

    try:
        ofn = sys.argv[2]
    except IndexError:
        xwm('Missing second argument: output filename (txt)')

    csv_to_txt(ifn, ofn)
