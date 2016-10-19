from django.http import JsonResponse

CODE_SUCCESS = 0
CODE_NOT_FOUND = 1
CODE_INVALID_SEMANTIC = 3
CODE_UNKNOWN = 4
CODE_USER_EXISTS = 5


def result(response, code=CODE_SUCCESS):
    return JsonResponse({
        'code': code,
        'response': response
        })

def result_not_found(response):
    return result(response, CODE_NOT_FOUND)

def result_user_exists(response):
    return result(response, CODE_USER_EXISTS)

def result_invalid_semantic(response):
    return result(response, CODE_INVALID_SEMANTIC)

def result_unknown(response):
    return result(response, CODE_UNKNOWN)




def model_dict(obj, description, remove=[]):
    res = {}
    for keyn, val in enumerate(obj):
        field = description[keyn][0]
        if field == 'date':
            val = date_normal(val)
        if field[0:2] == 'is':
            val = bool(val)

        if field in remove:                   # ? why it needs remove
            continue
        res[field] = val

    return res


def date_normal(date):
    if date is None:
        return ''
    return date.strftime('%Y-%m-%d %H:%M:%S')


def check_arg(val, allowed=[]):
    return val in allowed


def check_enum(enum, allowed=[]):
    for i in enum:
        if i not in allowed:
            return False
    return True