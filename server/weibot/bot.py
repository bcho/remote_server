#coding: utf-8

from server.base import db, logger
from server import imagesbin
from server.models import User
from server.queuer import reports, waitings, unknown
from server.translator.dictionary import s

from .current import bot


def repost(somethings, repost_id):
    '''repost a tweet'''
    resp = bot.post.t__re_add(content=somethings, reid=repost_id)
    return resp


def upload_image(somethings, image_name, someone):
    '''upload an image and @someone'''
    content = '@%s: %s' % (someone, somethings)
    image = imagesbin.get(image_name)
    resp = bot.upload.t__add_pic(content=content, pic=image)
    return resp


def send():
    report = reports.get()
    if report:
        #: is query all
        if report.type == 1 and report.obj == 'all':
            resp = upload_image(report.report, str(report.id),
                                report.user.name)
        else:
            resp = repost(report.report, report.tweet_id)
        reports.archive(report.id)
        logger.info('archived job <%d %s>' % (report.id, report.action))
        return resp
    else:
        return None


def handle_commands(commands):
    def _is_user(name):
        return db.session.query(User).filter(User.name == name).count() > 0

    for command in commands:
        if not waitings.in_queue(command.id) and _is_user(command.name) and\
                not unknown.in_queue(command.id):
            new_job = waitings.enqueue(command.text, command.id, command.name)
            if new_job:
                logger.info('found new job <%d %s>' % (
                                    new_job.id, new_job.action))
            else:
                unknown.enqueue(command.id, command.text)
                repost(s['unknowncommand'](), command.id)


def fetch():
    timeline = bot.get.statuses__mentions_timeline()
    mentions = timeline.data.info
    handle_commands(mentions)
