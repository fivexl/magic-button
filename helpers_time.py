import pytz
from datetime import datetime


def is_business_hours(timezone):
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    return True if now.hour > 8 and now.hour < 19 else False


def is_friday_evening(timezone):
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    return True if now.isoweekday() == 5 and now.hour > 14 else False


def current_time(timezone):
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    return "{}:{}:{}".format(now.hour, now.minute, now.second)


def generate_time_based_message(production_branches, branches, timezone):
    # if there is no overlap between branches to promote and production branches
    # then skip adding time based message
    if not list(set(production_branches) & set(branches)):
        return ''
    message = f'\n⚠️ It is {current_time(timezone)} in {timezone}.'
    if is_friday_evening(timezone):
        return (message
                + ' Deploying to production during Friday afternoon hours?'
                + ' *This a sure way to screw up your evening and potentialy weekend!*\n'
                + ' Make sure you are around to deal with consecuences')
    if is_business_hours(timezone):
        return message + ' *Business hours - think twice before deploying to production!*\n'
    return message + ' A good time to attempt deploy\n'
