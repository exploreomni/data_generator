def email_domain_from_url(url:str) -> str:
    pass1 = url.split('//')[1].split('/')[0]
    pass2 = pass1.replace('www.', '')
    return pass2

def email_handle_from_name(first_name:str, last_name:str, random_number:float=0.1) -> str:
    if random_number <= 0.1:
        return f'{first_name}.{last_name}'.lower()
    elif random_number <= 0.2:
        return f'{first_name[0]}{last_name}'.lower()
    elif random_number <= 0.3:
        return f'{first_name}{last_name}'.lower()
    elif random_number <= 0.4:
        return f'{first_name}{last_name[0]}'.lower()
    elif random_number <= 0.5:
        return f'{first_name[0]}{last_name[0]}'.lower()
    elif random_number <= 0.5:
        return f'{first_name}'.lower()
    elif random_number <= 0.6:
        return f'{last_name}'.lower()
    elif random_number <= 0.7:
        return f'{first_name[:4]}'.lower()
    else:
        return f'{first_name}.{last_name[:4]}'.lower()

    