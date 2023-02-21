import os
from datetime import datetime

from flask import jsonify, make_response, render_template
from flask_mail import Message

from frest.auth.models import Token
from frest.mail import mail


def send_email(sender, email, activation_code, title, template):
    msg = Message(title, sender=sender, recipients=[email])
    rest_link = os.getenv("FREST_URL", "http://localhost:8080/app")
    msg.html = render_template(template, link=rest_link, code=activation_code)
    mail.send(msg)


def http_call(data, status):
    return make_response(jsonify({"status": status, "result": data}), status)


def model_serialize(obj, params="", extend_model_for=[]):
    fields = {}
    params = params.split(",")

    for i in [f for f in dir(obj) if f in params]:
        if isinstance(obj.__getattribute__(i), datetime):
            fields[i] = obj.__getattribute__(i).strftime("%d/%m/%Y %H:%M")
        else:
            fields[i] = obj.__getattribute__(i)

    if len(extend_model_for) > 0:
        for key, value in fields.items():
            if isinstance(value, list):
                _l = []
                for v in value:
                    for i in extend_model_for:
                        if isinstance(v, i):
                            if hasattr(v, 'as_json'):
                                _l.append(v.as_json())
                            else:
                                _l.append(v)

                fields[key] = _l
            else:
                for i in extend_model_for:
                    if isinstance(value, i):
                        if hasattr(value, 'as_json'):
                            fields[key] = value.as_json()
                        else:
                            fields[key] = value

    return fields

def author_is_admin(request):
    """Returns true if the author of the request is an admin."""

    auth = request.headers.get("Authorization")
    token = Token.query.filter_by(string=auth).first()
    if token:
        return token.user.is_admin

    return False
