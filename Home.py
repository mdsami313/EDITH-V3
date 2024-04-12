import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from cwe import css

st.write(css, unsafe_allow_html=True)

if "signedout"  not in st.session_state:
    st.session_state["signedout"] = False
if 'signout' not in st.session_state:
    st.session_state['signout'] = False  

if 'username' not in st.session_state:
    st.session_state.username = ''
if 'useremail' not in st.session_state:
    st.session_state.useremail = ''

def hide_sidebar():
    st.markdown("""
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
    

def f(): 
    try:
        user = auth.get_user_by_email(email)
        print(user.uid)
        st.session_state.username = user.uid
        st.session_state.useremail = user.email
        
        global Usernm
        Usernm=(user.uid)
        
        st.session_state.signedout = True
        st.session_state.signout = True    
        
    except: 
        st.warning('Login Failed')

def t():
    st.session_state.signout = False
    st.session_state.signedout = False   
    st.session_state.username = ''  

if  not st.session_state["signedout"]: # only show if the state is False, hence the button has never been clicked
    choice = st.selectbox('Login/Signup',['Login','Sign up'])
    email = st.text_input('Email Address')
    password = st.text_input('Password',type='password')
    

    
    if choice == 'Sign up':
        username = st.text_input("Enter  your unique username")
        
        if st.button('Create my account'):
            user = auth.create_user(email = email, password = password,uid=username)
            
            # st.audio_countccess('Account created audio_countccessfully!')
            st.markdown('Please Login using your email and password')
            st.balloons()
    else:
        # st.button('Login', on_click=f)          
        st.button('Login', on_click=f)


def main():
    
    try:
        st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )
    except:
        pass

    st.write("# Welcome, I'm E.D.I.T.H 👋")

    st.image("hero-animation.gif")

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate('document-chatbot-8b13f-6877f0069a1d.json')
        default_app = firebase_admin.initialize_app(cred)
except:
    pass
if not st.session_state.signout:
    hide_sidebar()
    
if st.session_state.signout:
    main()
    with st.sidebar:
        st.button('Sign out', on_click=t)