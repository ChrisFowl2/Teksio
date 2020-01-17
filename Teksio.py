#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Teksio.
A new taskmanagementtool with a innovative concept.
© CCD.
'''

__author__ = 'Chris van den Hoorn'
__company__ = 'CCD'
__version__ = '0/0.0'

#Imports
import os
import csv
import datetime

#Errors
class TeksioError(Exception):
    '''Internal Teksio system error'''
    pass
class RegisterError(Exception):
    '''Expected value not present in register'''
    pass
class GhostError(Exception):
    '''Expected value not in teksie register, but is in sitio register'''
    pass
class DeleteError(Exception):
    '''Illegal to delete teksie in current situation'''
    pass

#Setting constants
newlinesymbol = '\n'
locations = {
    'Teksices':'Teksices.tkkcq',
    'Collections':'Collections.tkccq',
    'Sitio':'Sitio.tkscq'
}
if not os.path.exists(locations['Teksices']):
    open(locations['Teksices'], mode='w')
if not os.path.exists(locations['Collections']):
    open(locations['Collections'], mode='w')

#Functions
def Overview(mode='Teksices'):
    if not type(mode) is str:
        raise TypeError('Argument mode must be of type str when overviewing')
    if mode == 'Teksices':
        teksiefile = locations['Teksices']
    elif mode == 'Collections':
        teksiefile = locations['Collections']
    elif mode == 'all':
        teksiefile = locations['Sitio']
    else:
        raise ValueError('Argument mode must have one of the following values: Teksices, Collections, all; when overviewing')
    teksies = []
    with open(teksiefile, mode='r') as filetxt:
        filecsv = csv.reader(filetxt, delimiter='|')
        for line in filecsv:
            code = line[0]
            try:
                teksie = Teksio(code)
            except ValueError:
                try:
                    teksie = Collection(code)
                except ValueError:
                    raise GhostError('Not found teksie code in one of the registers when overviewing')
            teksies.append(teksie)
    teksies = tuple(teksies)
    return teksies

def UnitOverview(year=False, quarter=False, month=False, week=False, day=False, mode='Teksices'):
    def check(linelist):
        if type(year) is int:
            if not int(linelist[1]) == year:
                return False
        if type(quarter) is int:
            if not int(linelist[2]) == quarter:
                return False
        if type(month) is int:
            if not int(linelist[3]) == month:
                return False
        if type(week) is int:
            if not int(linelist[4]) == week:
                return False
        if type(day) is int:
            if not int(linelist[5]) == day:
                return False
        return True
    for x in (year, quarter, month, week, day):
        if not type(x) in (int, bool):
            raise TypeError('Unitarguments must be of type int or bool when overviewing a unit, conflicting value: '+str(x))
        if type(year) is bool and type(quarter) is bool and type(month) is bool and type(day) is bool:
            raise ValueError('One of the unitarguments must be of type int')
        if not type(mode) is str:
            raise TypeError('Argument mode must be of type str when overviewing a unit')
        if mode == 'Teksices':
            links_mode = True
            links_file = locations['Teksices']
        elif mode == 'Collections':
            links_mode = True
            links_file = locations['Collections']
        elif mode == 'all':
            links_mode = False
        else:
            raise ValueError('Argument mode must have one of the following values: Teksices, Collections, all; when overviewing a unit')
        teksies = []
        if links_mode:
            links = []
            with open(links_file, mode='r') as filetxt:
                filecsv = csv.reader(filetxt, delimiter='|')
                for line in filecsv:
                    links.append(line[0])
            with open(locations['Sitio']) as filetxt:
                filecsv = csv.reader(filetxt, delimiter='|')
                for line in filecsv:
                    if line[0] in links:
                        if check(line):
                            if mode == 'Teksices':
                                teksie = Teksio(line[0])
                            elif mode == 'Collections':
                                teksie = Collection(line[0])
                            else:
                                raise TeksioError('Invalid value for mode passed input check when overviewing a unit')
                            teksies.append(teksie)
        else:
            with open(locations['Sitio']) as filetxt:
                filecsv = csv.reader(filetxt, delimiter='|')
                for line in filecsv:
                    if check(line):
                        try:
                            teksie = Teksio(line[0])
                        except ValueError:
                            try:
                                teksie = Collection(line[0])
                            except ValueError:
                                raise GhostError('Not found teksie code in one of the registers when overviewing a unit')
                        teksies.append(teksie)
        teksies = tuple(teksies)
        return teksies

def Due():
    due = []
    teksices = Overview(mode='Teksices')
    for teksio in teksices:
        if teksio.sitio.Compare('>', teksio.collection.sitio):
            due.append(teksio)
    due = tuple(due)
    return due

def Expired():
    expired = []
    teksices = Overview(mode='Teksices')
    for teksio in teksices:
        if teksio.sitio.Expired():
            expired.append(teksio)
    expired = tuple(expired)
    return expired

#Classes
class Sitio():
    def Check(self, phase, year=None, quarter=None, month=None, week=None, day=None):
        if year == None:
            year = self.year
        if quarter == None:
            quarter = self.quarter
        if month == None:
            month = self.month
        if week == None:
            week = self.week
        if day == None:
            day = self.day
        if not type(phase) is str:
            raise TypeError('Argument phase must be of type str when checking Sitio data')
        try:
            year = str(year)
        except (TypeError, ValueError):
            raise TypeError('Argument year must be able to covert to type str when checking Sitio data')
        try:
            quarter = str(quarter)
        except (TypeError, ValueError):
            raise TypeError('Argument quarter must be able to covert to type str when checking Sitio data')
        try:
            month = str(month)
        except (TypeError, ValueError):
            raise TypeError('Argument month must be able to covert to type str when checking Sitio data')
        try:
            week = str(week)
        except (TypeError, ValueError):
            raise TypeError('Argument week must be able to covert to type str when checking Sitio data')
        try:
            day = str(day)
        except (TypeError, ValueError):
            raise TypeError('Argument day must be able to covert to type str when checking Sitio data')
        if not len(year) in (1, 2, 3, 4):
            raise ValueError('The year must have a length of 1, 2, 3, or 4 '+phase)
        if not len(quarter) == 1:
            raise ValueError('The quarter must have a length of 1 '+phase)
        if not len(month) in (1, 2):
            raise ValueError('The month must have a length of 1 or 2 '+phase)
        if not len(week) in (1, 2):
            raise ValueError('The week must have a length of 1 or 2 '+phase)
        if not len(day) == 1:
            raise ValueError('The day must have a length of 1 '+phase)
        try:
            year = int(year)
        except ValueError:
            raise ValueError('The year must be a number '+phase)
        try:
            quarter = int(quarter)
        except ValueError:
            raise ValueError('The quarter must be a number '+phase)
        try:
            month = int(month)
        except ValueError:
            raise ValueError('The month must be a number '+phase)
        try:
            week = int(week)
        except ValueError:
            raise ValueError('The week must be a number '+phase)
        try:
            day = int(day)
        except ValueError:
            raise ValueError('The day must be a number '+phase)
        if not year in range(0, 10000):
            raise ValueError('The year must be between 0 (0000) and 10000 (9999) '+phase)
        if not quarter in range(0, 5):
            raise ValueError('The quarter must be between 0 (0) and 5 (4) '+phase)
        if not month in range(0, 13):
            raise ValueError('The month must be between 0 (00) and 13 (12) '+phase)
        if not week in range(0, 54):
            raise ValueError('The week must be between 0 (00) and 54 (53) '+phase)
        if not day in range(0, 8):
            raise ValueError('The day must be between 0 (0) and 8 (7) '+phase)
        return True

    def Save(self, year=None, quarter=None, month=None, week=None, day=None, code=None, createline=False):
        if year == None:
            year = self.year
        if quarter == None:
            quarter = self.quarter
        if month == None:
            month = self.month
        if week == None:
            week = self.week
        if day == None:
            day = self.day
        if code == None:
            code = self.master.code
        if not type(year) is int:
            raise TypeError('Argument year must be of type int when saving Sitio data')
        if not type(quarter) is int:
            raise TypeError('Argument quarter must be of type int when saving Sitio data')
        if not type(month) is int:
            raise TypeError('Argument month must be of type int when saving Sitio data')
        if not type(week) is int:
            raise TypeError('Argument week must be of type int when saving Sitio data')
        if not type(day) is int:
            raise TypeError('Argument day must be of type int when saving Sitio data')
        if not type(code) is str:
            raise TypeError('Argument code must be of type str when saving Sitio data')
        if not type(createline) is bool:
            raise TypeError('Argument createline must be of type bool when saving Sitio data')
        self.Check('when saving Sitio data', year, quarter, month, week, day)
        year = str(year)
        quarter = str(quarter)
        month = str(month)
        week = str(week)
        day = str(day)
        while True:
            if len(year) == 4:
                break
            year = '0' + year
        if not len(month) == 2:
            month = '0' + month
        if not len(week) == 2:
            week = '0' + week
        newline = '|'.join((code, year, quarter, month, week, day)) + newlinesymbol
        if createline:
            with open(locations['Sitio'], mode='a', newline=newlinesymbol) as file:
                file.write(newline)
        else:
            with open(locations['Sitio'], mode='r') as file:
                lines = file.readlines()
            for linenumber, line in enumerate(lines):
                if line.startswith(code):
                    break
            else:
                raise ValueError('The master code ('+str(code)+') was not found in sitio register when saving Sitio data')
            lines[linenumber] = newline
            with open(locations['Sitio'], mode='w') as file:
                file.writelines(lines)
    
    def Acceptable(self, unit, year=None, quarter=None, month=None, week=None, day=None):
        if not type(unit) is str:
            raise TypeError('Argument unit must be of type str when checking acceptable values for Sitio')
        if year == None:
            year = self.year
        if quarter == None:
            quarter = self.quarter
        if month == None:
            month = self.month
        if week == None:
            week = self.week
        if day == None:
            day = self.day
        if not type(year) is int:
            raise TypeError('Argument year must be of type int when checking acceptable values for Sitio')
        if not type(quarter) is int:
            raise TypeError('Argument quarter must be of type int when checking acceptable values for Sitio')
        if not type(month) is int:
            raise TypeError('Argument month must be of type int when checking acceptable values for Sitio')
        if not type(week) is int:
            raise TypeError('Argument week must be of type int when checking acceptable values for Sitio')
        if not type(day) is int:
            raise TypeError('Argument day must be of type int when checking acceptable values for Sitio')
        self.Check('when checking acceptable values for Sitio', year, quarter, month, week, day)
        if unit == 'year':
            if week == 53:
                if day == 0:
                    years = []
                    for x in range(1, 10000):
                        day_first = datetime.date(x, 1, 1).weekday() + 1
                        day_last = datetime.date(x, 12, 31).weekday() + 1
                        if day_first == 4 or day_last == 4:
                            years.append(x)
                    return tuple(years)
                else:
                    years = []
                    for x in range(1, 10000):
                        i = 31
                        while True:
                            i -= 1
                            if datetime.datetime(x, 12, i).isocalendar()[1] != 53:
                                break
                        lastday = 31 - i
                        if day <= lastday:
                            years.append(x)
                    return tuple(years)
            else:
                return tuple(range(1, 10000))
        elif unit == 'quarter':
            if month == 0:
                if week == 0:
                    return (1, 2, 3, 4)
                else:
                    if week in range(1, 13):
                        return (1,)
                    elif week in range(13, 27):
                        return (2,)
                    elif week in range(27, 40):
                        return (3,)
                    elif week in range(40, 53):
                        return (4,)
                    else:
                        raise TeksioError('Invalid week number ('+str(week)+') passed SitioCheck when checking acceptable values for Sitio')
            else:
                if month in range(1, 4):
                    return (1,)
                elif month in range(4, 7):
                    return (2,)
                elif month in range(7, 10):
                    return (3,)
                elif month in range(10, 13):
                    return (4,)
                else:
                    raise TeksioError('Invalid month number ('+str(month)+') passed SitioCheck when checking acceptable values for Sitio')
        elif unit == 'month':
            if week == 0:
                if quarter == 0:
                    return tuple(range(1, 13))
                else:
                    return tuple({
                        1:range(1, 4),
                        2:range(4, 7),
                        3:range(7, 10),
                        4:range(10, 13)
                    }[quarter])
            else:
                months = []
                if year == 0:
                    for x in range(1, 10000):
                        for i in range(1, 13):
                            for q in range(1, 32):
                                try:
                                    weeknumber = datetime.datetime(x, i, q).isocalendar()[1]
                                except ValueError:
                                    pass
                                else:
                                    if weeknumber == week:
                                        if not i in months:
                                            months.append(i)
                else:
                    for x in range(1, 13):
                        for i in range(1, 32):
                            try:
                                weeknumber = datetime.datetime(year, x, i).isocalendar()[1]
                            except ValueError:
                                pass
                            else:
                                if weeknumber == week:
                                    if not x in months:
                                        months.append(x)
                return tuple(months)
        elif unit == 'week':
            if year == 0:
                if month == 0:
                    if quarter == 0:
                        if day == 0:
                            return tuple(range(0, 54))
                        elif day == 4:
                            return tuple(range(0, 54))
                        else:
                            return tuple(range(0, 53))
                    else:
                        if quarter == 4 and day in (0, 4):
                            return tuple(range(40, 54))
                        return tuple({
                            1:range(1, 13),
                            2:range(13, 27),
                            3:range(27, 40),
                            4:range(40, 53)
                        }[quarter])
                else:
                    weeks = []
                    if day == 0:
                        for x in range(1, 10000):
                            for i in range(1, 32):
                                try:
                                    weeknumber = datetime.datetime(x, month, i).isocalendar()[1]
                                except ValueError:
                                    pass
                                else:
                                    if not weeknumber in weeks:
                                        weeks.append(weeknumber)
                    else:
                        for x in range(1, 10000):
                            for i in range(1, 32):
                                try:
                                    date = datetime.datetime(x, month, i)
                                except ValueError:
                                    pass
                                else:
                                    if date.weekday() + 1 == day:
                                        weeknumber = date.isocalendar()[1]
                                        if not weeknumber in weeks:
                                            weeks.append(weeknumber)
                    return tuple(weeks)
            else:
                if month == 0:
                    if quarter == 0:
                        if day == 0:
                            day_first = datetime.date(year, 1, 1).weekday() + 1
                            day_last = datetime.date(year, 12, 31).weekday() + 1
                            if day_first == 4 or day_last == 4:
                                return(tuple(range(1, 54)))
                            else:
                                return(tuple(range(1, 53)))
                        else:
                            if day == 4:
                                day_first = datetime.date(year, 1, 1).weekday() + 1
                                day_last = datetime.date(year, 12, 31).weekday() + 1
                                if day_first == 4 or day_last == 4:
                                    return(tuple(range(1, 54)))
                                else:
                                    return(tuple(range(1, 53)))
                            else:
                                return(tuple(range(1, 53)))
                    else:
                        months = {
                            1:range(1, 4),
                            2:range(4, 7),
                            3:range(7, 10),
                            4:range(10, 13)
                        }[quarter]
                        weeks = []
                        if day == 0:
                            for x in months:
                                for i in range(1, 32):
                                    try:
                                        weeknumber = datetime.datetime(year, x, i).isocalendar()[1]
                                    except ValueError:
                                        pass
                                    else:
                                        if not weeknumber in weeks:
                                            weeks.append(weeknumber)
                        else:
                            for x in months:
                                for i in range(1, 32):
                                    try:
                                        date = datetime.datetime(year, x, i)
                                    except ValueError:
                                        pass
                                    else:
                                        if date.weekday() + 1 == day:
                                            weeknumber = date.isocalendar()[1]
                                            if not weeknumber in weeks:
                                                weeks.append(weeknumber)
                        return tuple(weeks)
                else:
                    weeks = []
                    if day == 0:
                        for x in range(1, 32):
                            try:
                                weeknumber = datetime.datetime(year, month, x).isocalendar()[1]
                            except ValueError:
                                pass
                            else:
                                if not weeknumber in weeks:
                                    weeks.append(weeknumber)
                    else:
                        for x in range(1, 32):
                            try:
                                date = datetime.datetime(year, month, x)
                            except ValueError:
                                pass
                            else:
                                if date.weekday() + 1 == day:
                                    weeknumber = date.isocalendar()[1]
                                    if not weeknumber in weeks:
                                        weeks.append(weeknumber)
                    return tuple(weeks)
        elif unit == 'day':
            if year == 0:
                if week == 53:
                    return tuple(range(1, 7))
                else:
                    return tuple(range(1, 8))
            else:
                if week == 1:
                    firstday = datetime.datetime(year, 1, 1).weekday() + 1
                    return tuple(range(firstday, 8))
                elif week == 52:
                    if datetime.datetime(year, 12, 31).isocalendar()[1] == 52:
                        x = 32
                        while True:
                            x -= 1
                            if datetime.datetime(year, 12, x).isocalendar()[1] != 52:
                                break
                        lastday = 32 - x
                        return tuple(range(1, lastday))
                    else:
                        return(tuple(range(1, 8)))
                elif week == 53:
                    x = 32
                    while True:
                        x -= 1
                        if datetime.datetime(year, 12, x).isocalendar()[1] != 53:
                            break
                    lastday = 32 - x
                    return tuple(range(1, lastday))
                else:
                    return tuple(range(1, 8))
        else:
            raise ValueError('Argument unit must have one of the following values: year, quarter, month, week, day; when checking acceptable values for Sitio')

    def Complete(self):
        for unit in ('year', 'quarter', 'month', 'week', 'day'):
            values = self.Acceptable(unit)
            if len(values) == 1:
                value = values[0]
                self.Plan(unit, value, complete=False)

    def Plan(self, unit, value, save=True, complete=True):
        if not type(unit) is str:
            raise TypeError('Argument unit must be of type str when planning with Sitio')
        if not type(value) is int:
            raise TypeError('Argument value must be of type int when planning with Sitio')
        if not type(save) is bool:
            raise TypeError('Argument save must be of type bool when planning with Sitio')
        if not type(complete) is bool:
            raise TypeError('Argument complete must be of type bool when planning with Sitio')
        if not unit in ('year', 'quarter', 'month', 'week', 'day'):
            raise ValueError('Argument unit must have one of the following values: year, quarter, month, week, day; when planning with Sitio')
        values_accepted = self.Acceptable(unit)
        if value in values_accepted:
            exec('self.'+unit+' = int('+str(value)+')')
            self.Save()
            if complete:
                self.Complete()
        else:
            values_accepted = list(values_accepted)
            for x in enumerate(values_accepted):
                values_accepted[x[0]] = str(x[1])
            values_accepted_formatted = ', '.join(values_accepted)
            raise ValueError('Argument value in combination with the unit '+unit+' must have one of the following values: '+values_accepted_formatted+'; when planning with Sitio')
    
    def Replan(self):
        sitiofile_newlines = []
        with open(locations['Sitio'], mode='r') as filetxt:
            filecsv = csv.reader(filetxt, delimiter='|')
            for line in filecsv:
                if not line[0] == self.master.code:
                    sitiofile_newlines.append(line)
        with open(locations['Sitio'], mode='w', newline='') as filetxt:
            filecsv = csv.writer(filetxt, delimiter='|')
            filecsv.writerows(sitiofile_newlines)
        self.__init__(self.master)

    def Compare(self, equation, contestant):
        if not type(equation) is str:
            raise TypeError('Argument equation must be of type str when comparing two sitici')
        if not type(contestant) is Sitio:
            raise TypeError('Argument contestant must be of type Sitio when comparing two sitici')
        if equation == '>':
            if self.year > contestant.year:
                return True
            elif self.year < contestant.year:
                return False
            else:
                if self.quarter > contestant.quarter:
                    return True
                elif self.quarter < contestant.quarter:
                    return False
                else:
                    if self.month > contestant.month:
                        return True
                    elif self.month < contestant.month:
                        return False
                    else:
                        if self.week > contestant.week:
                            return True
                        elif self.week < contestant.week:
                            return False
                        else:
                            if self.day > contestant.day:
                                return True
                            elif self.day < contestant.day:
                                return False
                            else:
                                return False
        elif equation == '<':
            if self.Compare('=', contestant):
                return False
            else:
                return not self.Compare('>', contestant)
        elif equation == '=':
            if self.year == contestant.year and self.quarter == contestant.quarter and self.month == contestant.month and self.week == contestant.week and self.day == contestant.day:
                return True
            else:
                return False
        else:
            raise ValueError('Argument equation must have one of the following values: >, <, =; when comparing two sitici')

    def Expired(self):
        if self.mode == 'teksio':
            if self.master.status in ('done', 'revoked'):
                return True
        now = datetime.datetime.now()
        now_year = now.year
        if now.month in range(1, 4):
            now_quarter = 1
        elif now.month in range(4, 7):
            now_quarter = 2
        elif now.month in range(7, 10):
            now_quarter = 3
        elif now.month in range(10, 13):
            now_quarter = 4
        else:
            raise TeksioError('Invalid month number given by datetime module when checking for expired')
        now_month = now.month
        now_week = now.isocalendar()[1]
        now_day = now.weekday() + 1
        if now_year > self.year and self.year != 0:
            return True
        if now_quarter > self.quarter and self.quarter != 0:
            return True
        if now_month > self.month and self.month != 0:
            return True
        if now_week > self.week and self.week != 0:
            return True
        if now_day > self.day and self.day != 0:
            return True
        return False
    
    def __init__(self, master):
        if type(master) is Teksio:
            mode = 'teksio'
        elif type(master) is Collection:
            mode = 'collection'
        else:
            raise TypeError('Argument master must be of type Teksio or Collection when initializing Sitio')
        newline = False
        with open(locations['Sitio'], mode='r') as file:
            while True:
                line = file.readline()
                if line.startswith(master.code):
                    break
                if not newlinesymbol in line:
                    newline = True
                    line = master.code + '|0000|0|00|00|0'
                    break
        line = line.replace(newlinesymbol, '')
        line_list = line.split('|')
        if not len(line_list) == 6:
            raise SyntaxError('The syntax in the sitio file is not accepted, at least the line with code '+str(master.code))
        code, year, quarter, month, week, day = line_list
        if not code == master.code:
            raise TeksioError('While initializing Sitio, the given code ('+str(master.code)+') and the resulting code ('+str(code)+') did not match')
        self.Check('in sitio register when initializing Sitio', year, quarter, month, week, day)
        self.master = master
        self.mode = mode
        self.year = int(year)
        self.quarter = int(quarter)
        self.month = int(month)
        self.week = int(week)
        self.day = int(day)
        if newline:
            self.Save(createline=True)


class Collection():
    def Change(self, attribute, value):
        if not type(attribute) is str:
            raise TypeError('Argument attribute must be of type str when changing attribute of Collection')
        if attribute == 'code':
            if not type(value) is str:
                raise TypeError('Argument value must be of type str when changing code of Collection')
        elif attribute == 'key':
            if not type(value) is str:
                raise TypeError('Argument value must be of type str when changing key of Collection')
        elif attribute == 'description':
            if not type(value) is str:
                raise TypeError('Argument value must be of type str when changing description of Collection')
        elif attribute == 'priority':
            if not type(value) is int:
                raise TypeError('Argument value must be of type int when changing priority of Collection')
        else:
            raise ValueError('Argument attribute must have one of these values: code, key, description, priority; when changing attribute of Collection')
        column = {
            'code':0,
            'key':1,
            'description':2,
            'priority':3
        }[attribute]
        with open(locations['Collections'], mode='r') as file:
            lines = file.readlines()
        for linenumber, line in enumerate(lines):
            if line.startswith(self.code):
                break
        else:
            raise RegisterError('Not found own code ('+self.code+') in collections register')
        line_list = line.split('|')
        if not len(line_list) == 4:
            raise SyntaxError('The syntax of the collections file is not accepted, at least the line with code '+self.code)
        line_list[column] = str(value)
        newline = '|'.join(line_list)
        if not newlinesymbol in newline:
            newline += newlinesymbol
        lines[linenumber] = newline
        with open(locations['Collections'], mode='w') as file:
            file.writelines(lines)
        if attribute == 'code':
            code = value
        else:
            code = self.code
        self.__init__(code)
    
    def Delete(self):
        with open(locations['Teksices'], mode='r') as filetxt:
            filecsv = csv.reader(filetxt, delimiter='|')
            for line in filecsv:
                if line[1] == self.code:
                    raise DeleteError('Illegal to delete a Collection if one or more teksices is part of the collection when deleting a collection')
        with open(locations['Collections'], mode='r') as file:
            collectionsfile_lines = file.readlines()
        with open(locations['Sitio'], mode='r') as file:
            sitiofile_lines = file.readlines()
        for index, line in enumerate(collectionsfile_lines):
            if line.startswith(self.code):
                collectionsfile_line = index
        for index, line in enumerate(sitiofile_lines):
            if line.startswith(self.code):
                sitiofile_line = index
        del collectionsfile_lines[collectionsfile_line]
        del sitiofile_lines[sitiofile_line]
        with open(locations['Collections'], mode='w') as file:
            file.writelines(collectionsfile_lines)
        with open(locations['Sitio'], mode='w') as file:
            file.writelines(sitiofile_lines)
    
    def FindTeksices(self):
        teksices = {}
        with open(locations['Teksices'], mode='r') as file:
            csvfile = csv.reader(file, delimiter='|')
            for row in csvfile:
                teksiocode = row[0]
                collectioncode = row[1]
                if collectioncode == self.code:
                    teksices[teksiocode] = Teksio(teksiocode)
        self.teksices = teksices

    def __init__(self, code=None, create=False, key=None, description=None, priority=None, findTeksices=True):
        if create:
            if key == None:
                raise ValueError('Define key when creating Collection')
            else:
                if not type(key) is str:
                    raise TypeError('Argument key must be of type str when creating Collection')
            if description == None:
                raise ValueError('Define description when creating Collection ')
            else:
                if not type(description) is str:
                    raise TypeError('Argument description must be of type str when creating Collection')
            if priority == None:
                raise ValueError('Define priority when creating Collection')
            else:
                if not type(priority) is int:
                    raise TypeError('Argument priority must be of type int when creating Collection')
            if code == None:
                with open(locations['Collections'], mode='r') as file:
                    try:
                        lastcode_line = file.readlines()[-1]
                    except IndexError:
                        lastcode_line = False
                if lastcode_line == False:
                    code = 'TC1'
                else:
                    lastcode = lastcode_line.split('|')[0]
                    lastnumber = int(lastcode.replace('TC', ''))
                    codenumber = lastnumber + 1
                    code = 'TC' + str(codenumber)
            entry = '|'.join((code, key, description, str(priority))) + newlinesymbol
            with open(locations['Collections'], mode='a') as file:
                file.write(entry)
            self.code = code
            self.key = key
            self.description = description
            self.priority = priority
        else:
            if code == None:
                raise ValueError('Define code when not creating Collection')
            else:
                if not type(code) is str:
                    raise TypeError('Argument code must be of type str when initializing Collection')
            with open(locations['Collections'], mode='r') as file:
                while True:
                    line = file.readline()
                    if line.startswith(code):
                        break
                    if not newlinesymbol in line:
                        raise ValueError('Argument code was not found in collections register')
            line = line.replace(newlinesymbol, '')
            try:
                code_line, key, description, priority = line.split('|')
            except ValueError:
                raise SyntaxError('The syntax in the collections file is not accepted, at least the line with code '+str(code))
            if code != code_line:
                raise TeksioError('While initializing Collection, the given code ('+str(code)+') and the resulting code ('+str(code_line)+') did not match')
            self.code = code
            self.key = key
            self.description = description
            self.priority = int(priority)
        self.sitio = Sitio(self)
        if findTeksices:
            self.FindTeksices()


class Teksio():
    def Change(self, attribute, value):
        if not type(attribute) is str:
            raise TypeError('Argument attribute must be of type str when changing attribute of Teksio')
        if attribute == 'code':
            if not type(value) is str:
                raise TypeError('Argument value must be of type str when changing code of Teksio')
        elif attribute == 'collection':
            if not type(value) is Collection:
                raise TypeError('Argument value must be of type Collection when changing code of Teksio')
            else:
                value = value.code
        elif attribute == 'key':
            if not type(value) is str:
                raise TypeError('Argument value must be of type str when changing key of Teksio')
        elif attribute == 'teksia':
            if not type(value) is str:
                raise TypeError('Argument value must be of type str when changing teksia of Teksio')
        elif attribute == 'status':
            if not type(value) is str:
                raise TypeError('Argument value must be of type str when changing status of Teksio')
        else:
            raise ValueError('Argument attribute must have one of these values: code, collection, key, teksia; when changing attribute of Teksio')
        column = {
            'code':0,
            'collection':1,
            'key':2,
            'teksia':3,
            'status':4
        }[attribute]
        with open(locations['Teksices'], mode='r') as file:
            lines = file.readlines()
        for linenumber, line in enumerate(lines):
            if line.startswith(self.code):
                break
        else:
            raise RegisterError('Not found own code ('+self.code+') in teksices register')
        line_list = line.split('|')
        if not len(line_list) == 5:
            raise SyntaxError('The syntax of the teksices file is not accepted, at least the line with code '+self.code)
        line_list[column] = str(value)
        newline = '|'.join(line_list)
        if not newlinesymbol in newline:
            newline += newlinesymbol
        lines[linenumber] = newline
        with open(locations['Teksices'], mode='w') as file:
            file.writelines(lines)
        if attribute == 'code':
            code = value
        else:
            code = self.code
        self.__init__(code)

    def Delete(self):
        with open(locations['Teksices'], mode='r') as file:
            teksicesfile_lines = file.readlines()
        with open(locations['Sitio'], mode='r') as file:
            sitiofile_lines = file.readlines()
        for index, line in enumerate(teksicesfile_lines):
            if line.startswith(self.code):
                teksicesfile_line = index
        for index, line in enumerate(sitiofile_lines):
            if line.startswith(self.code):
                sitiofile_line = index
        del teksicesfile_lines[teksicesfile_line]
        del sitiofile_lines[sitiofile_line]
        with open(locations['Teksices'], mode='w') as file:
            file.writelines(teksicesfile_lines)
        with open(locations['Sitio'], mode='w') as file:
            file.writelines(sitiofile_lines)
    
    def __init__(self, code=None, create=False, collection=None, key=None, teksia=None, status=None):
        if create:
            if collection == None:
                raise ValueError('Define collection when creating Teksio')
            else:
                if not type(collection) is Collection:
                    raise TypeError('Argument collection must be of type Collection')
            if key == None:
                raise ValueError('Define key when creating Teksio')
            else:
                if not type(key) is str:
                    raise TypeError('Argument key must be of type str')
            if teksia == None:
                raise ValueError('Define teksia when creating Teksio')
            else:
                if not type(teksia) is str:
                    raise TypeError('Argument teksia must be of type str')
            if status == None:
                raise ValueError('Define status when creating Teksio')
            else:
                if not type(status) is str:
                    raise TypeError('Argument status must be of type str')
            if code == None:
                with open(locations['Teksices'], mode='r') as file:
                    try:
                        lastcode_line = file.readlines()[-1]
                    except IndexError:
                        lastcode_line = False
                if lastcode_line == False:
                    code = 'TK1'
                else:
                    lastcode = lastcode_line.split('|')[0]
                    lastnumber = int(lastcode.replace('TK', ''))
                    codenumber = lastnumber + 1
                    code = 'TK' + str(codenumber)
            entry = '|'.join((code, collection.code, key, teksia, status)) + newlinesymbol
            with open(locations['Teksices'], mode='a') as file:
                file.write(entry)
            self.code = code
            self.collection = collection
            self.key = key
            self.teksia = teksia
            self.status = status
        else:
            if code == None:
                raise ValueError('Define code when not creating Teksio')
            else:
                if not type(code) is str:
                    raise TypeError('Argument code must be of type str')
            with open(locations['Teksices'], mode='r') as file:
                while True:
                    line = file.readline()
                    if line.startswith(code):
                        break
                    if not newlinesymbol in line:
                        raise ValueError('Argument code was not found in teksices register')
            line = line.replace(newlinesymbol, '')
            try:
                code_line, collection, key, teksia, status = line.split('|')
            except ValueError:
                raise SyntaxError('The syntax in the teksices file in not accepted, at least the line with code '+str(code))
            if code != code_line:
                raise TeksioError('While initializing Teksio, the given code ('+str(code)+') and the resulting search code ('+str(code_line)+') did not match')
            self.code = code
            self.collection = Collection(code=collection, findTeksices=False)
            self.key = key
            self.teksia = teksia
            self.status = status
        self.sitio = Sitio(self)