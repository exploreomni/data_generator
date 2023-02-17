import random
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


def consumer_email_domain():
    domains = {
        'gmail.com':45,'yahoo.com':10,'hotmail.com':10,'outlook.com':5,
        'icloud.com':5,'aol.com':3,'msn.com':3,'live.com':3,'comcast.net':2,'cox.net':2,
        'att.net':2,'verizon.net':1,'sbcglobal.net':1,'charter.net':1,'earthlink.net':0.5,'optonline.net':0.25,
        'frontier.com':0.01,'frontiernet.net':0.01,'mac.com':0.01,'me.com':0.01,'ymail.com':0.01,'bellsouth.net':0.001,
        'rocketmail.com':0.001,'roadrunner.com':0.001,'aim.com':0.001,'q.com':0.001,'juno.com':0.001,'windstream.net':0.001,
        'centurylink.net':0.001,'netzero.net':0.001,'netzero.com':0.001,'gmx.com':0.001,'mail.com':0.001,'protonmail.com':0.001,
        'yahoo.co.uk':0.001,'yahoo.com.au':0.001,'yahoo.com.br':0.001,'yahoo.com.mx':0.001,'yahoo.com.cn':0.001
    }
    return random.choices(list(domains.keys()), weights=list(domains.values()), k=1)[0]