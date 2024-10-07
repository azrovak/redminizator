from aiogram.utils.formatting import Bold, as_line, as_list

from config import redmine


def _get_issues():
    user = redmine.user.get('current')
    return user.issues


async def get_last_entries(count: int):
    user = redmine.user.get('current')
    l = []
    for i in (user.time_entries[:count]):
        l.append(Bold(f'Задача: {redmine.issue.get(i.issue.id).subject}({i.issue.id}) '))
        l.append(as_line(Bold('Дата'), f': {i.spent_on} ',
                         Bold('Часы'), f': {i.hours} ',
                         Bold('Комментарий'), f': {i.comments}')
                 )
    content = as_list(Bold('Последнии отметки времени'), *l)
    return content
