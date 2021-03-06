import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import abort

def get_bearer_token(request):
    bearer_token = request.headers.get("Authorization", None)
    if not bearer_token: # Token não encontrado.
        abort(401)
    
    parts = bearer_token.split()

    if parts[0].lower() != "bearer": # Header sem Bearer no Authorization
        abort(401)
    elif len(parts) == 1: # Header sem Token não encontrado
        abort(401)
    elif len(parts) > 2: # Header com mais de uma informação além do Token
        abort(401)
    
    bearer_token = parts[1]

    return bearer_token  


def send_mail(request):
    if request.method != "POST":
        abort(405)  # Retorna Method Not Allowed (HTTP 405) em qualquer verbo chamado além do POST

    bearer_token = get_bearer_token(request) # Recupera token para validação do header
    secret_key = os.environ.get("ACCESS_TOKEN")

    # Compara secret_key com bearer_token

    if secret_key != bearer_token:
        abort(401) # Retorna HTTP 401 - Unauthorized

    request_json = request.get_json(silent=True)
    parameters = ("sender", "receiver", "subject", "message")

    sender, receiver, subject, message = "", "", "", ""

    if request_json and all(k in request_json for k in parameters):
        sender = request_json["sender"]
        receiver = request_json["receiver"]
        subject = request_json["subject"]
        message = request_json["message"]
    else:
        abort(400) # Caso request_json não seja informado com todos os valores da tupla irá retornar HTTP 400 (Bad Request)

    message = Mail(
        from_email = sender,
        to_emails = receiver,
        subject = subject,
        html_content = message)


    # Enviar email com try/except (try/catch do C#) 

    try:
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        print(message)
        sg.send(message)  
        return 'OK', 200
    except Exception as e:  
        print(str(e))      
        return 'OK', 400
