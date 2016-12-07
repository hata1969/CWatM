# -------------------------------------------------------------------------
# Name:        Handling of timesteps and dates
# Purpose:
#
# Author:      P. Burek
#
# Created:     09/08/2016
# Copyright:   (c) burekpe 2016
# -------------------------------------------------------------------------


import os
import calendar
import datetime
import time as xtime
import numpy as np
from management_modules.globals import *
from management_modules.messages import *





def timemeasure(name,loops=0, update = False, sample = 1):
    timeMes.append(xtime.clock())
    if loops == 0:
        s = name
    else:
        s = name+"_%i" %(loops)
    timeMesString.append(s)
    return

# -----------------------------------------------------------------------
# Calendar routines
# -----------------------------------------------------------------------

def Calendar(input):
    """
    get the date from CalendarDayStart in the settings xml
    """
    try:
        date = float(input)
    except ValueError:
        d = input.replace('.', '/')
        d = d.replace('-', '/')
        year = d.split('/')[-1:]
        if len(year[0]) == 4:
            formatstr = "%d/%m/%Y"
        else:
            formatstr = "%d/%m/%y"
        if len(year[0]) == 1:
            d = d.replace('/', '.', 1)
            d = d.replace('/', '/0')
            d = d.replace('.', '/')
            print d
        date = datetime.datetime.strptime(d, formatstr)
        # value=str(int(date.strftime("%j")))
    return date


def datetoInt(dateIn,begin,both=False):

    date1 = Calendar(dateIn)

    if type(date1) is datetime.datetime:
         str1 = date1.strftime("%d/%m/%Y")
         int1 = (date1 - begin).days + 1
    else:
        int1 = int(date1)
        str1 = str(date1)
    if both: return int1,str1
    else: return int1




def checkifDate(start,end,spinup):

    begin = Calendar(binding['CalendarDayStart'])
    startdate = Calendar(binding['StepStart'])



    if type(startdate) is datetime.datetime:
        begin = startdate
    else:
        begin = begin + datetime.timedelta(days=startdate-1)


    # spinup date = date from which maps are written
    if binding[spinup].lower() == "none":  spinup = start
    else:
        if int(binding[spinup]) == 0:  spinup = start


    dateVar['intStart'],strStart = datetoInt(binding[start],begin,True)
    dateVar['intEnd'],strEnd = datetoInt(binding[end],begin,True)
    dateVar['intSpin'], strSpin = datetoInt(binding[spinup], begin, True)


    # test if start and end > begin
    if (dateVar['intStart']<0) or (dateVar['intEnd']<0) or ((dateVar['intEnd']-dateVar['intStart'])<0):
        strBegin = begin.strftime("%d/%m/%Y")
        msg="Start Date: "+strStart+" and/or end date: "+ strEnd + " are wrong!\n or smaller than the first time step date: "+strBegin
        raise CWATMError(msg)

    if (dateVar['intSpin'] < dateVar['intStart']) or (dateVar['intSpin'] > dateVar['intEnd']):
        strBegin = begin.strftime("%d/%m/%Y")
        msg="Spin Date: "+strSpin + " are wrong!\n or smaller/bigger than the first/last time step date: "+strBegin+ " - "+ strEnd
        raise CWATMError(msg)

    dateVar['dateBegin'] = begin
    dateVar['dateStart'] = begin + datetime.timedelta(days=dateVar['intSpin']-1)
    #dateVar['diffdays'] = dateVar['intEnd'] - dateVar['intStart'] + 1
    #dateVar['dateEnd'] = begin + datetime.timedelta(days=dateVar['diffdays']-1)
    dateVar['diffdays'] = dateVar['intEnd'] - dateVar['intSpin'] + 1
    dateVar['dateEnd'] = dateVar['dateStart'] + datetime.timedelta(days=dateVar['diffdays']-1)

    dateVar['curr'] = 0
    dateVar['currwrite'] = 0

    dateVar['datelastmonth'] = datetime.datetime(year=dateVar['dateEnd'].year, month= dateVar['dateEnd'].month, day=1) - datetime.timedelta(days=1)
    dateVar['datelastyear'] = datetime.datetime(year=dateVar['dateEnd'].year, month= 1, day=1) - datetime.timedelta(days=1)

    dateVar['checked'] = []
    dates = np.arange(dateVar['dateStart'], dateVar['dateEnd']+ datetime.timedelta(days=1), datetime.timedelta(days = 1)).astype(datetime.datetime)
    for d in dates:
        if d.day == calendar.monthrange(d.year, d.month)[1]:
            if d.month == 12:
                dateVar['checked'].append(2)
            else:
                dateVar['checked'].append(1)
        else:
            dateVar['checked'].append(0)

    dateVar['diffMonth'] = dateVar['checked'].count(1) + dateVar['checked'].count(2)
    dateVar['diffYear'] = dateVar['checked'].count(2)
    i=1



def timestep_dynamic():
    """
    Dynamic part of setting the date
    Current date is increasing, checking if beginning of month, year,
    """

    dateVar['currDate'] = dateVar['dateBegin'] + datetime.timedelta(days=dateVar['curr'])
    dateVar['currDatestr'] = dateVar['currDate'].strftime("%d/%m/%Y")
    dateVar['doy'] = int(dateVar['currDate'].strftime('%j'))
    dateVar['10day'] = int((dateVar['doy']-1)/10)

    dateVar['laststep'] = False
    if (dateVar['intStart'] + dateVar['curr']) == dateVar['intEnd']: dateVar['laststep'] = True

    dateVar['currStart'] = dateVar['curr'] + 1

    dateVar['curr'] += 1
    # count currwrite only after spin time
    if dateVar['curr'] >= dateVar['intSpin']:
        dateVar['currwrite'] += 1

    dateVar['currMonth'] = dateVar['checked'][:dateVar['currwrite']].count(1) + dateVar['checked'][:dateVar['currwrite']].count(2)
    dateVar['currYear'] = dateVar['checked'][:dateVar['currwrite']].count(2)

    # first timestep
    dateVar['newStart'] = dateVar['curr'] == 1
    dateVar['newMonth'] = dateVar['currDate'].day == 1
    dateVar['newYear'] = (dateVar['currDate'].day == 1) and (dateVar['currDate'].month == 1)
    dateVar['new10day'] = ((dateVar['doy'] - 1) / 10.0) == dateVar['10day']









