from pysolar.solar import *
import datetime
import numpy as np
date = datetime.datetime.now().replace(tzinfo=datetime.timezone.cet)


def getSunDir(lat,lon,date):
	degToRad=2*np.pi/360
	alt=get_altitude(lat, lon, date)*degToRad
	az=get_azimuth(lat, lon, date)*degToRad
	return (np.cos(alt)*np.cos(az),np.cos(alt)*np.sin(az), -np.sin(alt)) #dir to sun, N,E,down

def getSunlightRatio(lat,lon,windowOutWardNormalAzimuth,horizonHeight):
	windowN=(np.cos(windowOutWardNormalAzimuth),np.sin(windowOutWardNormalAzimuth), 0) #dir to sun, N,E,down
	
	d = start_date
	delta = datetime.timedelta(hours=1)
	while d <= end_date:
    	getSunDir(lat,lon,date)
    	d += delta

	np.dot(getSunDir(lat,long,date))
	return 1