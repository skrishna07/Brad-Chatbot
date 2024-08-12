import streamlit as st
import requests
from StreamlitChat import main

# Define the URL and any necessary parameters
url = "http://127.0.0.1:8000/login/"


# Function to get the CSRF token
response = requests.get(url)
st.title(response.cookies)
# Assuming the CSRF token is returned in a header or in the response body
csrf_token = response.cookies.get('csrftoken')  # Adjust this line based on where the token is
st.title(csrf_token)


#print(csrf_token)

# Function to send a POST request with the CSRF token
#def post_request_with_csrf(data):
 #   csrf_token = get_csrf_token()
 #   headers = {
 #       "X-CSRF-Token": csrf_token,
 #       "Content-Type": "application/json"
 #   }
 #   response = requests.post(url, json=data, headers=headers)
 #   return response


# Streamlit UI
is_login=False
# Create a title for the web app
st.title("Login Form")

# Create input fields for username and password
username = st.text_input("Username")
password = st.text_input("Password", type='password')

# Create a login button
if st.button("Login") and not(is_login):
    if username == "Admin" and password == "Pass@123":
        st.success("Logged in successfully!")
        is_login=True
        main()
    else:
        st.error("Invalid username or password")
