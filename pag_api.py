import requests


BASE_URL = 'https://www.sam-the-dev.com/pag_api'


def login(email, password):
    #Harden this up. sometimes get 500 error when the server needs to unseal
    #gets 404 out of nowhere
    # maybe just retry after a second?
    res = requests.post(f'{BASE_URL}/login', json={
        "email": email,
        "password": password
    })
    if res.status_code == 200:
        #no errors connecting to the server
        json = res.json()~
        if json['status']:
            #successful login
            return json['user']['token']
        else:
            #server worked, but creds didn't
            return False
    else:
        #server error likely
        return False
