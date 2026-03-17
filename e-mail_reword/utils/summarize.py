from utils.client import get_client

def original_emails(initial):

    system_prompt = """
    You're an assistant that make e-mails concise and professional in the workplace.
    """

    user_prompt_prefix = """
    Here are the contents of my current e-mail.Return a professional and concise version.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{user_prompt_prefix}\n\n{initial}"}
    ]
    
    client = get_client()
    

    response = client.chat.completions.create(model= "gpt-4o",
                                              messages = messages)

    return response.choices[0].message.content.strip()