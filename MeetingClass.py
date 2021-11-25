from datetime import datetime, timedelta, date

class MeetingClass(object):

    """Calculates and stores all data for the next meeting given a specific date"""

    def set_dates(self, current_date, weekday, accurance_in_month):
        """Calculates the next meeting and reminder dates """
            # First day of next month
            d = current_date.replace(day=1,month=current_date.month +1)
            # Get the first specific day of the month
            while d.weekday() != weekday:
                d += timedelta(days=1)
            #Add weeks 
            d += timedelta(days=(first_second_third_in_month-1)*7)

            # Check if the next meeting is within this month or more than 4weeks=28days away
            if d-current_date >= timedelta(days=28):
                # First day of this month
                d = current_date.replace(day=1)
                # Go to first specific day of the month
                while d.weekday() != weekday:
                    d += timedelta(days=1)
                #Add weeks 
                d += timedelta(days=(first_second_third_in_month-1)*7)

            self.meeting_date = d
            # We want a reminder one week before
            self.reminder_date = d-timedelta(days=-7)
            self.german_date = str(d.day)+"."+str(d.month)+"."+str(d.year)

            weekDays = ("Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag")
            self.day_name = weekDays(d.day())


class KoordinationsMeeting(MeetingClass):
    '''Das Koordinationsmeeting findet jeden 2. Mittwoch im Monat statt.'''

    def __init__(self):
        # 2 for Wednesday
        self.weekday = 2
        # 2 for second Wednesday in month
        self.accurance_in_month
        # Set all the important dates: self.meeting_date and reminder_date
        self.set_dates(date.today(),self.weekday,self.accurance_in_month)
        
        invitation_text = ["Nächste Woche findet das Koordinationsmeeting "+" "+self.day_name+", den  "+self.meeting_date+" "+"statt, bitte meldet euch kurz ob ihr kommt und welche Uhrzeit euch passt."]
        self.options = ["19 Uhr","21 Uhr", "Ich kann leider nicht"]

