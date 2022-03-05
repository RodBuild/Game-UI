import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk,Image
import pyrebase
import random
import io
import requests
import sys
import game_main
import database_config as dc


def show_frame(frame):
    frame.tkraise()
    #change it to string so you can use if
    str_frame = str(frame)
    if (str_frame == ".!frame"):
        #change window name to login in
        window.title("Game Name! - Login Page")
        #change window size
        window.geometry("350x350")
        window.minsize(350, 350)
        window.maxsize(350, 350)
    elif (str_frame == ".!frame2"):
        #change window name to sign up
        window.title("Game Name! - Signup Page")
        #change window size
        window.geometry("350x350")
        window.minsize(350, 350)
        window.maxsize(350, 350)
    elif (str_frame == ".!frame3"):
        #change window name to home
        window.title("Game Name! - Home Page")
        #change window size
        window.geometry("600x600")
        window.minsize(600, 600)
        window.maxsize(600, 600)
        #if (randomInt == 1):
        #    hp
    else:
        #change window name to game
        window.title("Game Name! - Game Page")

#----------------
# SETUP window 
window = tk.Tk()
window.title("Game Name! - Login Page")
window.geometry("350x350")
window.minsize(350, 350)
window.maxsize(350, 350)
window.rowconfigure(0,weight=1)
window.columnconfigure(0,weight=1)

#----------------------------------
# CREATE frames (pages to navigate)
LoginPage = tk.Frame(window,bg="red")
RegisterPage = tk.Frame(window,bg="Blue")
HomePage = tk.Frame(window,bg="yellow")
GamePage = tk.Frame(window,bg="green")
# LOOP that puts all frames on the screen
for frame in (LoginPage, RegisterPage, HomePage, GamePage):
    frame.grid(row=0,column=0,sticky='nsew')
# INITIALIZE first frame
show_frame(LoginPage)


#-------------#
#  VARIABLES  #
#-------------#
#database config
databaseConfig = dc.getConfig()
#initialize database
firebase = pyrebase.initialize_app(databaseConfig)
#firebase auth reference
authentication = firebase.auth()
#firebase storage reference
storage = firebase.storage()
#firebase database reference
database = firebase.database()

#fonts...
font1 = ("Yu Gothic UI Semibold",20)
font2 = ("Yu Gothic UI Semilight",20)
font3 = ("Bahnschrift", 25)
font4 = ("Malgun Gothic", 20)
font5 = ("Cascadia Mono SemiLight", 20)
font6 = ("Cascadia Mono SemiBold", 20)

#grab a background from FIREBASE storage to add it into the MainPage background
randomInt = random.randint(1,3)
url = storage.child("user_homepage_pictures").child("bg"+str(randomInt)).get_url(None)
res = requests.get(url)
image_bytes = io.BytesIO(res.content)

#-------------------------#
#  FUNCTIONS and CLASSES  #
#-------------------------#
class CurrentUser():
    #constructor
    def __init__(self, email, password, level, maxscore):
        self._email = email
        self._password = password
        self._level = level
        self._maxscore = maxscore
    #get username
    def getEmail(self):
        return self._email
    #set username
    def setEmail(self,email):
        self._email = email
    #get password
    def getPassword(self):
        return self._password
    #set password
    def setPassword(self,password):
        self._password = password
    #get level
    def getLevel(self):
        return self._level
    #set level
    def setLevel(self,level):
        self._level = level
    #get max score
    def getMaxScore(self):
        return self._maxscore
    #set max score
    def setMaxScore(self,score):
        self._maxscore = score

#current logged user
currentUser = CurrentUser("1","2","3","4")

#function to log in user
def login():
    email = lp_entry1.get()
    password = lp_entry2.get()
    #update currentUser
    currentUser.setEmail(email)
    currentUser.setPassword(password)
    #check with firebase
    try:
        authentication.sign_in_with_email_and_password(email,password)
        messagebox.showwarning("User found!", "You can continue to the next page!")
        pullFirebase()
        show_frame(HomePage)
    except:
        messagebox.showerror("User not found!", "Please check your input")
#function to sign up user
def signup():
    email = rp_entry1.get()
    password = rp_entry2.get()
    #update currentUser
    currentUser.setEmail(email)
    currentUser.setPassword(password)
    currentUser.setLevel(0)
    currentUser.setMaxScore(0)
    #add to the firebase
    try:
        authentication.create_user_with_email_and_password(email,password)
        messagebox.showwarning("Success!", "Your account has been created!")
        show_frame(LoginPage)
    except:
        messagebox.showerror("Error!", "There was a problem creating your account!")

#push to FIREBASE database
def pushFirebase():
    username = hp_entry1.get()
    title = varq.get()
    #create new data set with user input
    data = {'username':username, 'title': title, 'email':currentUser.getEmail()}
    #user_data hold all the current users in the database under the child of 'user_data'
    user_data = database.child('user_data').get()
    #if user gets into the homepage without logging in 😅😅
    if (currentUser.getEmail() == '1'):
        messagebox.showerror("ERROR!", "How did you get here without logging in?!?")
    #if username is missing, we throw an error
    elif (username != ""):
        #default that user does not exist
        exists = False
        #loop through users in the database
        for user in user_data.each():
            #if user exists, update
            if (user.val()['email'] == currentUser.getEmail()):
                database.child('user_data').child(user.key()).update(data)
                exists = True
                break
        #if does not exist, create new
        if (exists == False):
            database.child('user_data').push(data)
        #now that the new data is on the cloud database, lets add update the main page
        pullFirebase()
        #updateMainPage()
    else:
        messagebox.showwarning("Alert!", "Username cannot be empty!")

#pull to FIREBASE database | also a way of updating main page
def pullFirebase():
    # first database to pull - user data
    user_data = database.child('user_data').get()
    for user in user_data.each():
        if (user.val()['email'] == currentUser.getEmail()):
            hp_data.configure(text='All hail! ' + user.val()['username'] + ', the ' + user.val()['title'])
            break
    
    #second database to pull - user game
    game_data = database.child('user_game').get()
    found = False
    for user in game_data.each():
        if(user.val()['email'] == currentUser.getEmail()):
            # we update level and maxscore in currentUser
            #print(user.val()['level'])
            found = True
            currentUser.setLevel(user.val()['level'])
            currentUser.setMaxScore(user.val()['maxscore'])
            hp_stats.configure(text='Level: ' + str(user.val()['level']) + '\n' + 'Score: ' + str(user.val()['maxscore']))
            break
    # We can take go ahead and create a data entry for not found user
    if (found == False):
        data = {'email':currentUser.getEmail(), 'level': 0, 'maxscore': 0}
        database.child('user_game').push(data)

#to retireve data about the game - user level/user score
def gameUpdateStats():
    return 0


#start the game
def launchGame():
    x = game_main.Game()
    x.run()
    gameUpdateStats()
    
    #messagebox.showinfo("Patience", "Still on progress!")
    #show_frame(GamePage)

#-----------------------------------
# LOGIN PAGE CODE
#-----------------------------------
#background
lg_img = ImageTk.PhotoImage(Image.open("pictures/nature1.jpg"))
lg_back=tk.Label(LoginPage, image=lg_img)
lg_back.place(relheight=1,relwidth=1)
#main label
lp_title = tk.Label(LoginPage, text='Welcome Back Champion', font= font1, background='black',foreground='white')
lp_title.pack(side=tk.TOP,pady=5, fill=tk.X)
#Email label 
lp_label1 = tk.Label(LoginPage, text='Email', font=font4, background='#CA2E55',foreground='#F4D58D')
lp_label1.place(relx=0.36, rely=0.148, width=100)
#Email entry
lp_entry1 = tk.Entry(LoginPage, font=font2)
lp_entry1.pack(fill=tk.X, padx=5, pady=50)
#Password label
lp_label2 = tk.Label(LoginPage, text='Password', font=font4, background='#CA2E55',foreground='#F4D58D')
lp_label2.place(relx=0.28, rely=0.425, width=150)
#Password entry
lp_entry2 = tk.Entry(LoginPage, font=font2, show='*')
lp_entry2.pack(fill=tk.X, padx=5, pady=5)
#buttons
lp_btn1 = tk.Button(LoginPage, text='Log in', font=font2, background='#0FA3B1', command=lambda:login())
lp_btn1.place(relx=0.18,rely=0.75, height=50)
lp_btn2 = tk.Button(LoginPage, text='Sign up', font=font2, background='#0FA3B1', command=lambda:show_frame(RegisterPage))
lp_btn2.place(relx=0.52,rely=0.75, height=50)

#-----------------------------------
# REGISTER PAGE CODE
#-----------------------------------
#background
rp_img = ImageTk.PhotoImage(Image.open("pictures/night1.jpg"))
rp_back=tk.Label(RegisterPage, image=rp_img)
rp_back.place(relheight=1,relwidth=1)
#main label
rp_title = tk.Label(RegisterPage, text='Welcome New Champion', font= font1, background='black',foreground='white')
rp_title.pack(side=tk.TOP,pady=5, fill=tk.X)
#Email label 
rp_label1 = tk.Label(RegisterPage, text='Email', font=font4, background='#CA2E55',foreground='#F4D58D')
rp_label1.place(relx=0.36, rely=0.148, width=100)
#Email entry
rp_entry1 = tk.Entry(RegisterPage, font=font2)
rp_entry1.pack(fill=tk.X, padx=5, pady=50)
#Password label
rp_label2 = tk.Label(RegisterPage, text='Password', font=font4, background='#CA2E55',foreground='#F4D58D')
rp_label2.place(relx=0.28, rely=0.425, width=150)
#Password entry
rp_entry2 = tk.Entry(RegisterPage, font=font2, show='*')
rp_entry2.pack(fill=tk.X, padx=5, pady=5)
#buttons
rp_btn1 = tk.Button(RegisterPage, text='Create', font=font2, background='#0FA3B1', command=lambda:signup())
rp_btn1.place(relx=0.18,rely=0.75, height=50)
rp_btn2 = tk.Button(RegisterPage, text='<- Go back', font=font2, background='#0FA3B1', command=lambda:show_frame(LoginPage))
rp_btn2.place(relx=0.52,rely=0.75, height=50)


#-----------------------------------
# HOME PAGE CODE
#-----------------------------------
#background
hp_img = ImageTk.PhotoImage(Image.open(image_bytes))
hp_back=tk.Label(HomePage, image=hp_img)
hp_back.place(relheight=1,relwidth=1)
#main label
hp_title = tk.Label(HomePage, text='Ready to Start?', font= font1, background='black',foreground='white')
hp_title.pack(side=tk.TOP,pady=5, fill=tk.X)
#back button
hp_btn1 = tk.Button(HomePage, text='<- Go back', font=font3, background='#0FA3B1', command=lambda:show_frame(LoginPage))
hp_btn1.place(relx=0.02,rely=0.1, height=45)
#username label
hp_label1 = tk.Label(HomePage, text='Username', font=font4, background='#CA2E55',foreground='#F4D58D')
hp_label1.place(relx=0.02, rely=0.2, width=150)
#username entry
hp_entry1 = tk.Entry(HomePage, font=font2)
hp_entry1.place(relx=0.32,rely=0.2, width=380)
#title label
hp_label2 = tk.Label(HomePage, text='Title', font=font4, background='#CA2E55',foreground='#F4D58D')
hp_label2.place(relx=0.02, rely=0.3, width=150)
#title options entry [ADD username, THE [TITLE]]
titles = ["Calm","Dame", "Sir", "Master", "Pacifist", "Unbeatable"]
varq = tk.StringVar(HomePage)
varq.set(titles[0])
hp_opMenu = tk.OptionMenu(HomePage, varq, *titles)
hp_opMenu.place(relx=0.32,rely=0.3, width=380)
#submit button
hp_btn2 = tk.Button(HomePage, text='Submit', font=font3, background='#e8dd15', command=lambda:pushFirebase())
hp_btn2.place(relx=0.4,rely=0.4, height=45)
#user data label
hp_data = tk.Label(HomePage,text='Waiting for update...', font=font4, background='#305cc2',foreground='#F4D58D')
hp_data.place(rely=0.5,relwidth=1)
#user_stats label
hp_stats = tk.Label(HomePage,text=('Level: 999'+'\n'+'Score: 9999999'),font=font2, background='white',borderwidth=1,relief='solid')
hp_stats.place(relx=0.5,rely=0.65,anchor=tk.CENTER,relwidth=0.3)

#start game button
hp_game_btn = tk.Button(HomePage, text='Start Game', font=font3, background='#e8dd15', command=lambda:launchGame())
hp_game_btn.pack(side=tk.BOTTOM, pady=10)
#-----------------------------------
# GAME PAGE CODE
#-----------------------------------


#---------------
# START window
window.mainloop()