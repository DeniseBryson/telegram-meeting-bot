from datetime import datetime, timedelta, date
import os
import time
from telegram import Bot
from telegram.ext import (
        CallbackContext
        )

class MeetingClass(object):
    """Calculates and stores all data for the next meeting given a specific date"""
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self._running = True
        # Should there be a poll to determine the time
        self._poll = False

    def set_dates(self, weekday, occurance_in_month):
        """Calculates the next meeting and reminder dates """
        # First day of next month
        today = date.today()
        if today.month == 12:
            d = today.replace(day=1,month=1, year = date.today().year + 1)
        else:
            d = today.replace(day=1,month=today.month +1)
        # Get the first specific day of the month
        while d.weekday() != self.weekday:
            d += timedelta(days=1)
        #Add weeks 
        d += timedelta(days=(self.occurance_in_month-1)*7)

        # Check if the next meeting is after today within this month 
        # First day of this month
        d_this_month = today.replace(day=1)
        # Go to first specific day of the month
        while d_this_month.weekday() != weekday:
            d_this_month += timedelta(days=1)
        #Add weeks 
        d_this_month += timedelta(days=(self.occurance_in_month-1)*7)
        # Is the meeting this month after today or is it today?
        if d_this_month-today >= timedelta(days=0):
            d = d_this_month

        meeting_date = d
        # We want a reminder one week before
        invitation_date = d-timedelta(days=-7)
        german_date = str(d.day)+"."+str(d.month)+"."+str(d.year)

        weekDays = ("Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag")
        day_name = weekDays[d.weekday()]

        return meeting_date, invitation_date, german_date, day_name

    def organize(self, bot):
        '''Waits for the specific dates and send reminder and invitation'''

        while self._running:
            if self._poll:
                self.organize_with_poll()
            else:
                date_was_in_the_past = self.wait_until(self.invitation_date)
                if not date_was_in_the_past:
                    self.send_message(self.invitation_text, bot)
                
                date_was_in_the_past = self.wait_until(self.meeting_date)
                if not date_was_in_the_past:
                    self.send_message(self.reminder, bot)
            
                #Calculate dates for the next meeting
                self.update_dates()

        if not self._running:
            self.send_message("Meeting was aborted", bot)

    def organize_with_poll(self):
        #TODO organize with poll
        pass

    def send_message(self, text: str, bot: Bot) -> bool:
        '''Sends a message to the Chat of this Meeting'''        
        bot.send_message(self.chat_id, text)

    def wait_until(self, end_date):
        while self._running:
            diff = (end_date - date.today())
            if diff < timedelta(days=0): 
                return True
            elif diff == timedelta(days=0):
                return False
            else:
                time.sleep(60*60*6)
        return True

    def stop_meeting(self, thread):
        self._running = False
        self.delete_meeting()

    def update_dates(self):
        '''Updates invitation_date and meeting_date for next meeting'''

        # First day of next month
        today = date.today()

        if today.month == 12:
            d = today.replace(day=1,month=1, year = date.today().year + 1)
        else:
            d = today.replace(day=1,month=today.month +1)

        # Get the first specific day of the month
        while d.weekday() != self.weekday:
            d += timedelta(days=1)
        #Add weeks 
        d += timedelta(days=(self.occurance_in_month-1)*7)

        # Check if the next meeting is after today within this month 
        # First day of this month
        d_this_month = today.replace(day=1)
        # Go to first specific day of the month
        while d_this_month.weekday() != self.weekday:
            d_this_month += timedelta(days=1)
        #Add weeks 
        d_this_month += timedelta(days=(self.occurance_in_month-1)*7)
        # Is the meeting this month after today or is it today?
        if d_this_month-today >= timedelta(days=0):
            d = d_this_month

        self.meeting_date = d
        # We want a reminder one week before
        self.invitation_date = d-timedelta(days=7)
        self.german_date = str(d.day)+"."+str(d.month)+"."+str(d.year)

        weekDays = ("Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag")
        self.day_name = weekDays[d.weekday()]

    def change_dates(self, weekday, occurance_in_month):
        self.weekday = weekday
        self.occurance_in_month = occurance_in_month
        self.update_dates()

    def delete_meeting(self):
        '''Reads in all meeting objects and delet the aborted one then save it back'''
        meetings = []
        meeting_file = "./meetingobjects/meetings.p"
        with (open(meeting_file, "rb")) as openfile:
            while True:
                try:
                    meeting = pickle.load(openfile)
                    if not meeting.name == self.name:
                        meetings.append(meeting)
                except EOFError:
                    break

        os.remove(meeting_file)
        
        # Write new meeting file without the deleted meeting
        for meeting in meetings:
            with open(meeting_file,'wb') as mf:
                pickle.dump( meeting, mf)

class KoordinationsMeeting(MeetingClass):
    '''Das Koordinationsmeeting findet jeden 2. Mittwoch im Monat statt.'''

    def __init__(self, chat_id):
        #Sets chat_id and maybe more
        super(KoordinationsMeeting, self).__init__(chat_id)
        self.name = "koordination"
        # 2 for Wednesday
        self.weekday = 2
        # 2 for second Wednesday in month
        self.occurance_in_month = 2
        # Set all the important dates: self.meeting_date and invitation_date
        self.meeting_day,\
        self.invitation_date,\
        self.german_date,\
        self.day_name \
            = self.set_dates(self.weekday, self.occurance_in_month)
        self.time = "21.00 Uhr"
        
        self.invitation_text = ['''Hallo, 
            Am %s, den %s, findet das  Koordinationstreffen statt.
            Wir starten um %s Uhr!

            Wie gehen wieder Einzeln die Teilnehmerinnen durch um zu Erfahren was es neues gibt im Verein und was passiert ist in letzter Zeit. Macht euch im Vorfeld vielleicht Gedanken zu den folgenden Punkten.
            * Was muss in der großen Gruppe besprochen werden.
            * Relevante Informationen für die große Gruppe.
            * Wie erkläre ich meinen Inhalt so, dass auch Außenstehende ihn verstehen? :)

            Alle Vereinsmitglieder sind herzlich eingeladen!! Falls ihr  etwas vorstellen wollt meldet euch doch bitte bei Lukas damit ich euch einplanen kann!

            Hier schon mal das Pad:
            https://pad2.opensourceecology.de/Koordinationstreffen-2021'''%(self.day_name, self.time, self.german_date)]
        self.options = ["19 Uhr","21 Uhr", "Ich kann leider nicht"]

        self.reminder_text = ["Eine kurze Erinnerung, dass heute das Koordinationsmeeting stattfindet. Wir treffen uns um 21 Uhr hier: https://meet.openculture.agency/r/OSEG-Conference "]

    def poll(self):
        #message = context.bot.send_poll(
        #    update.effective_chat.id,
        #    text,
        #    options,
        #    is_anonymous=False,
        #    allows_multiple_answers=True,
        #)
        pass

class OThing(MeetingClass):
    '''OTing findet ersten Mittwoch im Monat statt.'''

    def __init__(self, chat_id):
        #Sets chat_id and maybe more
        super(OTing, self).__init__(chat_id)
        self.name = "othing"
        # 2 for Wednesday
        self.weekday = 2
        # 2 for second Wednesday in month
        self.occurance_in_month = 1
        # Set all the important dates: self.meeting_date and invitation_date
        self.set_dates(self.weekday,self.occurance_in_month)
        
        self.invitation_text = ['''Nächste Woche %s, den %s, ist wieder OThing-Zeit für alle die Lust haben! Hier ist der link zum pad:
https://md.opensourceecology.de/OSEG_Online_Thing_2021
Um 21 Uhr gehts los!

Hier ist der link zum Raum:
https://meet.openculture.agency/r/OSEG-Conference'''%(self.day_name, self.german_date)]

        self.reminder_text = ["Eine kurze Erinnerung, dass heute das OThing stattfindet. Wir treffen uns um 21 Uhr hier: https://meet.openculture.agency/r/OSEG-Conference "]
