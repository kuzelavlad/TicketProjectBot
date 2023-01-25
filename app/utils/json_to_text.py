def convert_to_text(json_data: dict) -> str:
    msg_text = ""
    for field, value in json_data.items():
        msg_text += f"{field.capitalize()}: {value}\n"

    return msg_text

def convert_to_text_ticket(json_data: dict) ->str:
    ticket_html = ""
    for field, value in json_data.items():
        ticket_html += f"{field.capitalize()}: {value}\n"

    return ticket_html