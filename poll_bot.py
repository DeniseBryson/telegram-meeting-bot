#Code used from https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/pollbot.py

import logging
import datetime
import pickle
from MeetingClass import KoordinationsMeeting 
from threading import Thread


from telegram import (
    Poll,
    ParseMode,
    KeyboardButton,
    KeyboardButtonPollType,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    PollAnswerHandler,
    PollHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    """Inform user about what this bot can do"""
    update.message.reply_text(
            ''' With \koordination I can start organising the Koordinationsmeeting in this group.'''
    )

def koordination(update: Update, context: CallbackContext, date_of_meeting: date) -> None:
    "Startet Pool für die Uhrzeit und sendet Einladung"

    # update.effective_chat.id, update.effective_message.id
    next_meeting = KoordinationsMeeting(update.effective_chat.id)
    save_meeting(next_meeting)
    t = Thread(target=next_meeting.organize, args=(context), daemon = True)
    t.start()

    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {update.effective_chat.id: next_meeting}
    context.bot_data.update(payload)


def othing(update: Update, context: CallbackContext, date_of_meeting: date) -> None:
    '''Organisiert das Othing in dem er auf die Klasse zurueckgreift'''

    # update.effective_chat.id, update.effective_message.id
    next_meeting = OThing(update.effective_chat.id)
    save_meeting(next_meeting)
    t = Thread(target=next_meeting.organize, args=(context), daemon = True)
    t.start()

    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {update.effective_chat.id: next_meeting}
    context.bot_data.update(payload)

def change_dates_of_meeting():
    #TODO
    pass

def load_running_meetings():
    #for meeting in open pickle:
    #TODO
    pass

def stop_meeting(update: Update, context: CallbackContext):
    meeting = context.bot_data[update.effective_chat.id]
    meeting.stop_meeting()

def create_meeting():
    #TODO
    pass

def receive_poll_answer(update: Update, context: CallbackContext) -> None:
    """Summarize a users poll vote"""
    answer = update.poll_answer
    poll_id = answer.poll_id
    user = update.effective_user
    print("\n User: ", user)
    print("\n Answer: ", update.poll_answer)
    print("Poll Options: " , update.poll.options)
    try:
        options = context.bot_data[poll_id]["options"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return

    #Add user object to the list of its answer to store the result
    # Go over all options
    for key in context.bot_data[poll_id]["voters_by_option"].keys():
        # Go through all answer of the user, multiple answers a possible
        for option_id in answer.option_ids:
            selected_option = options[option_id]
            if key == selected_option:
                context.bot_data[poll_id]["voters_by_option"][key].append(user)
    print("\n Result:", context.bot_data[poll_id]["voters_by_option"])
    context.bot_data[poll_id]["total_voter_count"] += 1

def stop_poll(poll_id, context: CallbackContext):
    """Stops poll and publishes the invitation and delets the poll from memory"""
    tag = "Dienstag"
    options = context.bot_data[poll_id]["options"]
    context.bot.stop_poll(
        context.bot_data[poll_id]["chat_id"], context.bot_data[poll_id]["message_id"]
    )
    votes = [context.bot_data[poll_id]["voters_by_option"][option] for idx, option in enumerate(options)]
    if votes[0] >= votes[1]:
        time = options[0]
    else:
        time = option[1]

    #Publish the invitation
    message = ["Das Koordinationsmeeting findet am "+tag+ " um "+ time + " statt." ]
    context.bot.send_message(
        context.bot_data[poll_id]["chat_id"],
        message,
        parse_mode=ParseMode.HTML
    )

    #Delete the poll to avoid confusion
    del context.bot_data[poll_id]

def quiz(update: Update, context: CallbackContext) -> None:
    """Send a predefined poll"""
    questions = ["1", "2", "4", "20"]
    message = update.effective_message.reply_poll(
        "How many eggs do you need for a cake?", questions, type=Poll.QUIZ, correct_option_id=2
    )
    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    payload = {
        message.poll.id: {"chat_id": update.effective_chat.id, "message_id": message.message_id}
    }
    context.bot_data.update(payload)

def poll_old(update: Update, context: CallbackContext) -> None:
    """Sends a predefined poll"""
    questions = ["Good", "Really good", "Fantastic", "Great"]
    message = context.bot.send_poll(
        update.effective_chat.id,
        "How are you?",
        questions,
        is_anonymous=False,
        allows_multiple_answers=True,
    )
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)

def receive_quiz_answer(update: Update, context: CallbackContext) -> None:
    """Close quiz after three participants took it"""
    # the bot can receive closed poll updates we don't care about
    if update.poll.is_closed:
        return
    if update.poll.total_voter_count == 3:
        try:
            quiz_data = context.bot_data[update.poll.id]
        # this means this poll answer update is from an old poll, we can't stop it then
        except KeyError:
            return
        context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])

def preview(update: Update, context: CallbackContext) -> None:
    """Ask user to create a poll and display a preview of it"""
    # using this without a type lets the user chooses what he wants (quiz or poll)
    button = [[KeyboardButton("Press me!", request_poll=KeyboardButtonPollType())]]
    message = "Press the button to let the bot generate a preview for your poll"
    # using one_time_keyboard to hide the keyboard
    update.effective_message.reply_text(
        message, reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=True)
    )

def receive_poll(update: Update, context: CallbackContext) -> None:
    """On receiving polls, reply to it by a closed poll copying the received poll"""
    actual_poll = update.effective_message.poll
    # Only need to set the question and options, since all other parameters don't matter for
    # a closed poll
    update.effective_message.reply_poll(
        question=actual_poll.question,
        options=[o.text for o in actual_poll.options],
        # with is_closed true, the poll/quiz is immediately closed
        is_closed=True,
        reply_markup=ReplyKeyboardRemove(),
    )

def help_handler(update: Update, context: CallbackContext) -> None:
    """Display a help message"""
    update.message.reply_text("Use /quiz, /poll or /preview to test this bot.")

def return_date_of_meeting_next_month(day,first_second_third_in_month):
    '''Returns the meeting date and the date of one week before to send the reminder'''
    # First day of next month
    d = date.today().replace(day=1,month=date.today().month +1 )
    # Get the first specific day of the month
    while d.weekday() != day:
        d += timedelta(days=1)
    #Add weeks 
    if first_second_third_in_month-1 > 0:
        d += timedelta(days=first_second_third_in_month*7)

    return d, d-timedelta(days=-7)

def read_token(file):
    '''Reads the token from file and returns it'''
    with open(file) as tf:
        token = tf.read()
    return token

def save_meeting(meeting):
    '''Saves meeting to file for later use'''
    file = "./meetingobjects/meetings.p"
    with open(file,'wb') as mf:
        pickle.dump( meeting, mf)

def main() -> None:
    """Run bot."""
    token = read_token("token.txt")
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('koordination', koord))
    dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
    dispatcher.add_handler(CommandHandler('quiz', quiz))
    dispatcher.add_handler(PollHandler(receive_quiz_answer))
    dispatcher.add_handler(CommandHandler('preview', preview))
    dispatcher.add_handler(MessageHandler(Filters.poll, receive_poll))
    dispatcher.add_handler(CommandHandler('help', help_handler))

    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
