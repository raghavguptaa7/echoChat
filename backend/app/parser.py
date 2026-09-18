import re
from datetime import datetime

MESSAGE_PATTERN = re.compile(
    r"^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+"
    r"(\d{1,2}:\d{2})\s*([APap][Mm])?\s*-\s"
    r"([^:]+):\s(.*)$"
)


def parse_chat(file_content: str):
    messages = []
    current_message = None

    for line in file_content.splitlines():
        match = MESSAGE_PATTERN.match(line)

        if match:
            if current_message:
                messages.append(current_message)

            date, time, am_pm, sender, message = match.groups()

            timestamp_text = f"{date} {time}"
            if am_pm:
                timestamp_text += f" {am_pm}"

            current_message = {
                "timestamp": timestamp_text,
                "sender": sender.strip(),
                "message": message.strip()
            }

        elif current_message and line.strip():
            current_message["message"] += f"\n{line.strip()}"

    if current_message:
        messages.append(current_message)

    return messages