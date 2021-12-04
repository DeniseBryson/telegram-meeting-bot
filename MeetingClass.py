from datetime import datetime, timedelta, date

class MeetingClass(object):
    """Calculates and stores all data for the next meeting given a specific date"""
    def __init__(self, chat_id):
        self.chat_id = chat_id

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

    def organize(self, context: CallbackContext):
        '''Waits for the specific dates and send reminder and invitation'''

        date_was_in_the_past = self.wait_until(self.reminder_date)
        if not date_was_in_the_past:
            self.send_message(self, context, self.invitation_text)
        
        date_was_in_the_past = self.wait_until(self.meeting_date)
        if not date_was_in_the_past:
            self.send_message(self, context, self.reminder)

    def send_message(self, context: CallbackContext, text) -> bool:
        '''Sends a message to the Chat of this Meeting'''        
        context.bot.send_message(self.chat_id, text)

    def wait_until(self, end_date):
        while True:
            diff = (end_date - date.today())
            if diff < timedelta(days=0): 
                return 1
            elif diff == timedelta(days=1):
                return 0
            else:
                time.sleep(60*60*12)

    def stop_meetings(self, thread):
        pass

class KoordinationsMeeting(MeetingClass):
    '''Das Koordinationsmeeting findet jeden 2. Mittwoch im Monat statt.'''

    def __init__(self, chat_id):
        #Sets chat_id and maybe more
        super(KoordinationsMeeting, self).__init__(chat_id)
        # 2 for Wednesday
        self.weekday = 2
        # 2 for second Wednesday in month
        self.accurance_in_month = 2
        # Set all the important dates: self.meeting_date and reminder_date
        self.set_dates(date.today(),self.weekday,self.accurance_in_month)
        
        self.invitation_text = ['Hallo,
Am %s, den %s, findet das  Koordinationstreffen statt.
Wir starten um 21 Uhr!

Wie gehen wieder Einzeln die Teilnehmerinnen durch um zu Erfahren was es neues gibt im Verein und was passiert ist in letzter Zeit. Macht euch im Vorfeld vielleicht Gedanken zu den folgenden Punkten.
* Was muss in der großen Gruppe besprochen werden.
* Relevante Informationen für die große Gruppe.
* Wie erkläre ich meinen Inhalt so, dass auch Außenstehende ihn verstehen? :)

Alle Vereinsmitglieder sind herzlich eingeladen!! Falls ihr  etwas vorstellen wollt meldet euch doch bitte bei Lukas damit ich euch einplanen kann!

Hier schon mal das Pad:
https://pad2.opensourceecology.de/Koordinationstreffen-2021'%(self.day_name, self.german_date)]
        self.options = ["19 Uhr","21 Uhr", "Ich kann leider nicht"]

        self.reminder_text = ["Eine kurze Erinnerung, dass heute das Koordinationsmeeting stattfindet. Wir treffen uns um 21 Uhr hier: https://meet.openculture.agency/r/OSEG-Conference "]

class OTing(MeetingClass):
    '''OTing findet ersten Mittwoch im Monat statt.'''

    def __init__(self, chat_id):
        #Sets chat_id and maybe more
        super(OTing, self).__init__(chat_id)
        # 2 for Wednesday
        self.weekday = 2
        # 2 for second Wednesday in month
        self.accurance_in_month = 1
        # Set all the important dates: self.meeting_date and reminder_date
        self.set_dates(date.today(),self.weekday,self.accurance_in_month)
        
        self.invitation_text = ["Nächste Woche %s, den %s, ist wieder OThing-Zeit für alle die Lust haben! Hier ist der link zum pad:
https://md.opensourceecology.de/OSEG_Online_Thing_2021
Um 21 Uhr gehts los!

Hier ist der link zum Raum:
https://meet.openculture.agency/r/OSEG-Conference"%(self.day_name, self.german_date)]

        self.reminder_text = ["Eine kurze Erinnerung, dass heute das OThing stattfindet. Wir treffen uns um 21 Uhr hier: https://meet.openculture.agency/r/OSEG-Conference "]
