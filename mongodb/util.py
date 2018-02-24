# import time
import json
import copy
import apiai

CLIENT_ACCESS_TOKEN = ''


def question(q):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()

    request.query = q

    if request.query == "exit":
        return 0

    response = request.getresponse()

    string = response.read()
    string = string.decode("utf-8")

    string_j = json.loads(string)

    return string_j


def dateTime(date_time):
    '''
    handle different date formats
    '''

    # format ['2017-06-24', '12:00:00/16:00:00']

    if (len(date_time) == 2):
        date, time = date_time[0], date_time[1]
        year, month, day = date.split("-")

        start_time, end_time = time.split("/")
        hour, minute, second = start_time.split(":")

        start = {"date": {"year": year, "month": month, "day": day},
                 "time": {"hour": hour, "minute": minute, "second": second}}

        hour, minute, second = end_time.split(":")

        end = {"date": {"year": year, "month": month, "day": day},
               "time": {"hour": hour, "minute": minute, "second": second}}

        return {"start": start, "end": end}

    start = date_time[0].split("/")[0]

    # format ['2017-06-24']

    if (start == date_time[0] and len(date_time) == 1):

        year, month, day = start.split("-")
        hour, minute, second = "00", "00", "00"
        start = {"date": {"year": year, "month": month, "day": day},
                 "time": {"hour": hour, "minute": minute, "second": second}}
        end = {"date": {"year": year, "month": month, "day": day},
               "time": {"hour": hour, "minute": minute, "second": second}}

    # format

    else:

        date, time = start.split("T")
        year, month, day = date.split("-")

        hour, minute, second = time.split("Z")[0].split(":")

        start = {"date": {"year": year, "month": month, "day": day},
                 "time": {"hour": hour, "minute": minute, "second": second}}

        end = date_time[0].split("/")[1]
        date, time = end.split("T")
        year, month, day = date.split("-")
        hour, minute, second = time.split("Z")[0].split(":")

        end = {"date": {"year": year, "month": month, "day": day},
               "time": {"hour": hour, "minute": minute, "second": second}}

    return {"start": start, "end": end}


def scheduling(timedate, employees, name):
    '''
    timedate : date and time to check
    Amy : object with person data
    '''

    # select date and time unavailable

    year = str(timedate["start"]["date"]["year"])
    month = str(timedate["start"]["date"]["month"])
    if list(month)[0] == '0':
        month = "".join(list(month)[1])
    day = str(timedate["start"]["date"]["day"])

    work_time = employees[name]["free_time"][year][month][day]

    hour = timedate["start"]["time"]["hour"]
    minute = timedate["start"]["time"]["minute"]
    second = timedate["start"]["time"]["second"]
    s = hour + ":" + minute + ":" + second

    hour = timedate["end"]["time"]["hour"]
    minute = timedate["end"]["time"]["minute"]
    second = timedate["end"]["time"]["second"]
    e = hour + ":" + minute + ":" + second

    d = year + "/" + month + "/" + day

    c = True
    # check all the booker dates
    print(name, (s, e), d)
    print()
    for w_t in work_time:
        print("Unavailable periods:", w_t)

    print()
    for w_t in work_time:

        work_hour_start, work_minute_start, work_second_start = w_t[0].split(":")
        work_hour_end, work_minute_end, work_second_end = w_t[1].split(":")

        # check if the unavailable period intersect my request

        if timedate["start"]["time"]["hour"] >= work_hour_start and timedate["end"]["time"]["hour"] <= work_hour_end:
            c = False

        if timedate["start"]["time"]["hour"] == work_hour_end:

            if timedate["start"]["time"]["minute"] > work_minute_end:
                c = False
            else:
                print(name, "Available Soon")
                break

        if timedate["end"]["time"]["hour"] == work_hour_start:

            if timedate["end"]["time"]["minute"] < work_minute_start:
                c = False
            else:
                print(name, "Available but no delay")
                break

    if c is False:
        print("No available")

    return (name, (s, e), d)


####################################################################################################

class Employees:
    def __init__(self):

        self.day = {str(i): list() for i in range(1, 32)}
        self.months = {str(i): copy.deepcopy(self.day) for i in range(1, 13)}
        self.date = {'2017': copy.deepcopy(self.months)}

        self.person = {'name': '', 'tid': '', 'job': '', 'team': [], 'free_time': copy.deepcopy(self.date),
                       'mail': '', 'working_on': '', 'updates': 1, 'office': ''}

        # working_at={}
        # employees = {}

    def create_person(self, employees, working_at, name='', tid='', job='', team=[], mail='', working_on='', updates=1,
                      office='', t=1):

        # global working_at

        pers = {'name': '', 'tid': '', 'job': '', 'team': [], 'free_time': copy.deepcopy(self.date),
                'mail': '', 'working_on': '', 'updates': 1, 'office': ''}

        if t == 1:
            print("-Data new employees")
            print("\n")
            if name == '':
                print('  insert name: ')
                name = input()
            if tid == '':
                print('  insert id: ')
                tid = input()
            if job == '':
                print('  insert job: ')
                job = input()
            if team == []:
                print('  insert team: ')
                team = input().split()
            if mail == '':
                print('  insert mail: ')
                mail = input()
            if working_on == '':
                print('  insert working_on: ')
                working_on = input()
            if office == '':
                print('  insert office: ')
                office = input()

            print("End insertion data new employees-")
            print("\n")

        pers['name'] = name
        pers['tid'] = tid
        pers['job'] = job
        pers['team'] = team
        pers['mail'] = mail
        pers['working_on'] = working_on
        pers['updates'] = 1
        pers['office'] = office

        if (working_on in working_at):
            working_at[working_on].append(name)
        else:
            working_at[working_on] = [name]

        employees[name] = copy.deepcopy(pers)

        return employees, working_at

    def insert_time(self, employees, person, year, month, day, time_start, time_end):

        employees[person]['free_time'][str(year)][str(month)][str(day)].append((str(time_start), str(time_end)))

        return employees

    def working_on(self, Person):
        return Person['working_on']


######################################################################################################

def put_data():
    working_at = {}
    employees = {}

    e = Employees()

    employees, working_at = e.create_person(employees, working_at, name='manuel', job='ninja',
                                            tid=idm, team=['norman', 'george'], working_on='project_Y', t=0)
    employees = e.insert_time(employees, "manuel", 2017, 6, 24, '10:00:00', '12:00:00')

    employees, working_at = e.create_person(employees, working_at, name='george', job='georger',
                                            team=['norman', 'manuel'],
                                            tid=idg, working_on='project_Y', t=0)
    employees = e.insert_time(employees, "george", 2017, 6, 24, '20:00:00', '22:00:00')

    employees, working_at = e.create_person(employees, working_at, name='norman', job='engineer',
                                            team=['george', 'manuel'],
                                            tid=idn, working_on='project_Y', t=0)
    employees = e.insert_time(employees, "norman", 2017, 6, 24, '18:00:00', '20:00:00')

    return employees, working_at


##########################################################################################################

# -*- coding: UTF-8 -*-

def ugly_time(data, employees, name):
    date_time = data["result"]["parameters"]["date-time"]

    timedate = dateTime(date_time)
    scheduling(timedate, employees, name)

    return None
