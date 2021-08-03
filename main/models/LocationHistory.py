from django.contrib import messages
from django.db import models
from datetime import datetime
import main.constants as const
import pandas as pd
import json
import numpy as np
from datetime import datetime
import math

from django.conf import settings
from django.contrib.sessions.models import Session

# Create your models here.
class LocationHistory(models.Model):
    user = models.ForeignKey( settings.AUTH_USER_MODEL, default=1, verbose_name="User", on_delete=models.SET_DEFAULT, )    
#    session = models.ForeignKey(Session, on_delete=models.SET_NULL, blank=True, null=True)
    session_key = models.CharField(max_length=300, blank=True, null=True)
    zip_file = models.FileField(upload_to=const.LOC_HIST_FILE_SUBDIR)
    dir = models.CharField(max_length=300, blank=True)
    sem_dir = models.CharField(max_length=300, blank=True)
    point_file = models.CharField(max_length=300, blank=True)
    uploaded_at = models.DateTimeField(default=datetime.now, blank=True)
    
    dfp = pd.DataFrame()

    
    def __str__(self):
        return self.zip_file.name
        
        
    def locHistDictToDF(self, locHistDict):

        t1 = datetime.now()
        print('Start locHistDictToDF()')

        newLoc = []
        data_days = set() #set of all days with data
        
        locHistDict = locHistDict['locations']

        for loc in locHistDict:
            #print('old\n');
            #print(json.dumps(loc, indent=2), l)
#            if(TIME_FRAME[0] <= datetime.fromtimestamp( float(loc['timestampMs']) / 1000.0) <= TIME_FRAME[1]):
#            indentation adjusted below for removing the if statement above

            data_days.add(datetime.fromtimestamp( float(loc['timestampMs']) / 1000.0).date()) #adding to set of unique days with data

            if 'activity' in loc:
                blankLoc = loc.copy()
                del blankLoc['activity']
                firstSameTime = True
                for act in loc['activity']:
                    #print('for activity', loc['timestampMs'],' ', int(act['timestampMs']),'\n')
                    newLoc.append(blankLoc.copy()) #*****
                    newLoc[-1]['activity'] = [act]
                    
                    
                    if( not (act['activity'][0]['type'] in set(IGNORE_ACTIVITY_TYPE) ) ):
                        newLoc[-1]["IS_ANY_ACT"] = 1  #****
                        for i in range(0, min( len( act['activity'] ), const.KEEP_ACTIVITY_TYPE_COUNT)):
                            #newLoc[-1]['act' + str(i)] = act['activity'][i]['type']
                            #newLoc[-1]['prob' + str(i)] = act['activity'][i]['confidence']
                            newLoc[-1][act['activity'][i]['type'] + '_CONF'] = act['activity'][i]['confidence']
    #                        unqActName.add(act['activity'][i]['type'])
                            #print("act['activity']: ", act['activity'], "   act['activity'][i]: ", act['activity'][i])

#                    if float(loc['timestampMs']) - ACTIVITY_TIME_DELTA  < float(act['timestampMs']) and float(loc['timestampMs']) + ACTIVITY_TIME_DELTA > float(act['timestampMs'] and not firstSameTime):
                    if float(loc['timestampMs']) - ACTIVITY_TIME_DELTA  < float(act['timestampMs']) and float(loc['timestampMs']) + ACTIVITY_TIME_DELTA > float(act['timestampMs']) and not firstSameTime: #repair appearent code error
                        #print('same time\n')
                    #    newLoc.append(blankLoc.copy())
                    #    newLoc[-1]['activity'] = [act]


                        firstSameTime = False
                        
                    else:
                        #print('diff time\n')
                    #    newLoc.append(blankLoc.copy())
                    #    newLoc[-1]['activity'] = [act]
                        newLoc[-1]['timestampMs'] = act['timestampMs']
                        
                    #print('new\n');
                    #print(json.dumps(newLoc[-1], indent=2), ' ', len(newLoc))
                
                if firstSameTime: #no activity at location time, need to include data point for location time
                    newLoc.append(blankLoc.copy())
                    #print('new\n');
                    #print(json.dumps(newLoc[-1], indent=2), ' ', len(newLoc))
                
            else:   #no activity 
                newLoc.append(loc.copy())
                #print('new\n')
                #print(json.dumps(newLoc[-1], indent=2), ' ', len(newLoc))
                
        
        data_days_c = len(data_days)
#        loc_delta_t = TIME_FRAME[1] - TIME_FRAME[0]
#        time_frame_days_c = loc_delta_t.days
                
#        print('time_frame_days_c:', time_frame_days_c)
        print('data_days:', data_days_c)
               
        newLoc = sorted(newLoc, key=lambda loc: loc['timestampMs'])
        
        self.dfp = pd.DataFrame(newLoc)

   
        #basic unit conversion
        self.dfp = self.dfp.astype({'timestampMs': 'int64'})
        self.dfp['timestampMs'] = self.dfp['timestampMs'] / 1000
        self.dfp['latitudeE7'] = self.dfp['latitudeE7'] / 10000000
        self.dfp['longitudeE7'] = self.dfp['longitudeE7'] / 10000000
        self.dfp.rename(columns = {'timestampMs':'timestampSec', 'latitudeE7':'lat', 'longitudeE7':'lng'}, inplace = True)
        self.dfp['time_stamp'] = pd.to_datetime(self.dfp['timestampSec'], unit='s')

        t = datetime.now() - t1
        print("locHistDictToDF() end time, before data cleaning:", t)


#        dfp = calcPointColumns(dfp)
        self.calcPointColumns()

#        dfp = pointDataCleaning(dfp)

        self.dfp.drop(0, inplace=True)
        self.dfp.reset_index(drop=True, inplace=True)

        self.dfp.to_csv(r'Loc Test.csv')


#        return [data_days_c, time_frame_days_c, self.dfp]
        return [data_days_c, self.dfp]


    def calcPointColumns(self):

        t1 = datetime.now()
        print("Calc Point Columns start")
        
        self.dfp['t_before'] = self.dfp['timestampSec'] - self.dfp['timestampSec'].shift(1) 
        self.dfp['d_before'] = self.pointDistance(self.dfp['lat'].values, self.dfp['lng'].values, self.dfp['lat'].shift(1).values, self.dfp['lng'].shift(1).values)
        self.dfp['v_before_mtps'] = self.dfp['d_before'] / self.dfp['t_before'] * 1000 #meters per second
        self.dfp['v_before_mtps'].fillna(0, inplace=True)
        self.dfp['accel'] = ( self.dfp['v_before_mtps'] - self.dfp['v_before_mtps'].shift(1) ) / ( 1/2 * (self.dfp['t_before'] + self.dfp['t_before'].shift(1)) )
    #    self.dfp['v_calc'] = self.dfp['velocity'].where(self.dfp['velocity'].notnull(), self.dfp['v_before_mtps'].where((self.dfp['v_before_mtps'] > 0.5) & (self.dfp['v_before_mtps'].shift(-1) > 0.5), 0))
        self.dfp['bearing'] = self.bearing(self.dfp['lat'].shift(1).values, self.dfp['lng'].shift(1).values, self.dfp['lat'].values, self.dfp['lng'].values)
        self.dfp['bearing_chg'] = float('nan')
        self.dfp['bearing_chg'].where(  ~( (self.dfp['v_before_mtps'] > const.V_STOP_MAX) & (self.dfp['v_before_mtps'].shift(-1) > const.V_STOP_MAX) ), abs((self.dfp['bearing'] - self.dfp['bearing'].shift(-1) + 360 + 180) % 360 - 180), inplace=True)
        self.dfp['bearing_chg_all'] = abs((self.dfp['bearing'] - self.dfp['bearing'].shift(-1) + 360 + 180) % 360 - 180)
        self.dfp['d_northing'] = self.dfp['d_before'] * np.cos( np.deg2rad( self.dfp['bearing'] ) )
        self.dfp['d_easting'] = self.dfp['d_before'] * np.sin( np.deg2rad( self.dfp['bearing'] ) )
        self.dfp['v_northing'] = self.dfp['d_northing'] / self.dfp['t_before'] * 1000 #meters per second
        self.dfp['v_easting'] = self.dfp['d_easting'] / self.dfp['t_before'] * 1000 #meters per second

    #    self.dfp['v_lat_before'] = np.abs( self.dfp['lat'] - self.dfp['lat'].shift(1) ) / self.dfp['t_before'] #degrees per second
    #    self.dfp['v_lng_before'] = np.abs( self.dfp['lng'] - self.dfp['lng'].shift(1) ) / self.dfp['t_before'] #degrees per second

        t = datetime.now() - t1
        print("Calc Point Columns end time:", t)

#        return dfp
        return

    # Define a basic Haversine distance formula
    def pointDistance(self, lat1, lng1, lat2, lng2):
        lat1, lng1, lat2, lng2 = map(np.deg2rad, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1 
        dlng = lng2 - lng1 
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlng/2)**2
        c = 2 * np.arcsin(np.sqrt(a)) 
        dist = const.EARTH_RADIUS_KM * c
        return dist

    def bearing(self, lat1, lng1, lat2, lng2):
        lat1, lng1, lat2, lng2 = map(np.deg2rad, [lat1, lng1, lat2, lng2])
        dlng = (lng2 - lng1)
        y = np.sin(dlng) * np.cos(lat2)
        x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlng)
        brng = np.arctan2(y, x)
        brng = np.rad2deg(brng)
        brng = brng % 360
    #    brng = 360 - brng # count degrees clockwise - remove to make counter-clockwise
        return brng



