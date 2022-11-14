import WSR98DIQFile

def read_DualPol(filename, station_lon=None, station_lat=None, station_alt=None):
    """
    :param filename:  radar basedata filename
    :param station_lon:  radar station longitude //units: degree east
    :param station_lat:  radar station latitude //units:degree north
    :param station_alt:  radar station altitude //units: meters
    """
    return WSR98DIQFile.DualPolData(filename, station_lon, station_lat, station_alt)


file = r'../data-test/Z9002_20220624_005007_10_CDX.IQ'
PRD = read_DualPol(file)























