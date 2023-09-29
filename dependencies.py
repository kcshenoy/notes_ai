import streamlit as st
import streamlit_authenticator as stauth
import re
import datetime
import os
from dotenv import main
from deta import Deta
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

main.load_dotenv()

deta = Deta(os.getenv('DETA_API_KEY'))

def insert_user(email, username, password):
    db = deta.Base('notes_users')
    date_joined = str(datetime.datetime.now())
    return db.put({'key': email, 'username': username, 'password': password, "date_joined": date_joined})

def validate_email(email):
    valid = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+') 

    if re.fullmatch(valid, email):
        return True
    else:
        return False
    
def validate_username(user):
    valid = "^[a-zA-Z0-9]*$"
    if re.match(valid, user):
        return True
    else:
        return False

def fetch_users():
    db = deta.Base('notes_users')
    users = db.fetch()
    return users.items

def get_emails():
    db = deta.Base('notes_users')
    users = db.fetch()
    emails = []
    for user in users.items:
        emails.append(user['key'])
    return emails

def get_usernames():
    db = deta.Base('notes_users')
    users = db.fetch()
    usernames = []
    for user in users.items:
        usernames.append(user['username'])
    return usernames

def sign_up():
    db = deta.Base('notes_users')
    with st.form(key='signup', clear_on_submit=True):
        st.subheader(':blue[Sign Up]')
        email = st.text_input(':blue[Email]', placeholder='Enter Email')
        username = st.text_input(':blue[Username]', placeholder='Enter Username')
        password1 = st.text_input(':blue[Password]', placeholder='Enter Password', type='password')
        password2 = st.text_input(':blue[Password]', placeholder='Confirm Password', type='password')

        if email:
            if validate_email(email):
                if email not in get_emails():
                    if validate_username(username):
                        if username not in get_usernames():
                            if len(username) >= 2:
                                if len(password1) >= 6:
                                    if password1 == password2:
                                        hashed_pw = stauth.Hasher([password2]).generate()
                                        st.success("Account Creation Successful")
                                        insert_user(email, username, hashed_pw[0])
                                        
                                    else:
                                        st.warning("Passwords Do Not Match")
                                else:
                                    st.warning("Password is too short")
                            else:
                                st.warning("Username is too short")
                        else:
                            st.warning("Username already exists")
                    else:
                        st.warning("Invalid Username")
                else:
                    st.warning("Email already in use")
            else:
                st.warning("Invalid Email")
        else:
            st.warning("Please enter Email")

        st.form_submit_button('Sign Up')
