import pyttsx3
from decouple import config
import speech_recognition as sr
from random import choice
from utils import *

import requests
from datetime import datetime
import pywhatkit as kit
import wikipedia

USERNAME = config("USER")
BOTNAME = config("BOTNAME")

engine = pyttsx3.init("sapi5")

#set rate
engine.setProperty("rate", 190)

#set volume
engine.setProperty("volume", 1.0)

#set voice (female)
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)

#recognizer
r = sr.Recognizer()

#retry statement
retry = "Sorry, I could not understand"

#math symbol
math_symbol = ["+", "-", "*", "/"]

#text to speech conversion
def speak(text):
    """used to speak whatever text is passed to it"""

    engine.say(text)
    engine.runAndWait()

def take_user_input():
    """get the user input"""
    with sr.Microphone(device_index=1) as source:
        print("Listening....")
        r.pause_threshold = 1
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            return audio
        except sr.WaitTimeoutError:
            print("Timeout occurred while listening.")
            return None
        except Exception as e:
            print("An error occurred while listening:", e)
            return None

def recognize(audio):
    print("Recognizing...")
    query = r.recognize_google(audio, language="en").lower()

    return query

def greet_user():
    """greets the user according to the time"""

    hour = datetime.now().hour
    if hour < 12:
        speak("Good Morning %s" % (USERNAME))
    elif hour >= 12 and hour < 16:
        speak("Good afternoon %s" % (USERNAME))
    elif hour >= 16:
        speak("Good Evening %s" % (USERNAME))
    speak("I am %s. How may I assist you?" % (BOTNAME))

def play_on_youtube(video):
    """search a YouTube video on the topic from the user input"""

    speak("I'm on it")

    kit.playonyt(video)

def search_on_wikipedia(query):
    """search up information about the subject"""

    results = wikipedia.summary(query, sentences=2)
    return results

def time():
    """get the current time"""

    hour = datetime.now().hour
    minute = datetime.now().minute
    time_of_day = "AM"

    if hour > 12:
        hour -= 12
        time_of_day = "PM"

    return "%d:%d %s" % (hour, minute, time_of_day)

def date():
    """get the current date"""

    months = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
    days = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th", 7: "7th", 8: "8th", 9: "9th", 10: "10th", 11: "11th", 12: "12th", 13: "13th", 14: "14th", 15: "15th", 16: "16th", 17: "17th", 18: "18th", 19: "19th", 20: "20th", 21: "21th", 22: "22th", 23: "23th", 24: "24th", 25: "25th", 26: "26th", 27: "27th", 28: "28th", 29: "29th", 30: "30th", 31: "31th"}

    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day

    return "%s %s, %d" % (months[month], days[day], year)

def get_latest_news():
    """search for headline news"""

    news_headlines = []
    newsAPIKey = config("NEWS_API_KEY")
    res = requests.get("https://newsapi.org/v2/top-headlines?country=in&apiKey=%s&category=general" % (newsAPIKey)).json()
    articles = res["articles"]
    for article in articles:
        news_headlines.append(article["title"])
    return news_headlines[:5]

def get_weather_report(city):
    """get the current weather of the city"""

    open_weather_app_ID = config("OPENWEATHER_APP_ID")
    res = requests.get("http://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s&units=metric" % (
    city, open_weather_app_ID)).json()
    weather = res["weather"][0]["main"]
    temperature = res["main"]["temp"]
    feels_like = res["main"]["feels_like"]

    return weather, "%.2f℃" % (temperature), "%.2f℃" % (feels_like)

def calculation(query):
    """calcuate the equation"""
    equation = ""

    for i in query:
        if i.isnumeric() == True or i == "." or i in math_symbol:
            equation += i

    answer = eval(equation)

    if answer == int(answer):
        return "It is %d" % (answer)
    else:
        return "It is %.2f" % (answer)

def measurement_conversion(num, unit1, unit2):
    """convert one unit to another"""

    if num == int(num):
        num = int(num)
    else:
        num = float(num)

    measurements = {
        "g-kg": 0.001, "kg-g": 1000,
        "kg-lb y"
        "": 2.20462, "lb-kg": 0.453592,
        "cm-m": 0.01, "m-cm": 100,
        "m-km": 0.001, "km-m": 1000,
        "m-ft": 3.28084, "ft-m": 0.3048
    }

    unit_conversion = unit1 + "-" + unit2

    if unit_conversion in measurements:
        conversion = num * measurements[unit1 + "-" + unit2]

        if conversion == int(conversion):
            return "It is %d %s" % (conversion, unit2)
        else:
            return "It is %.2f %s" % (conversion, unit2)
    else:
        return "This conversion is not in the system"

def run():
    """takes user input, recognizes it using Speech Recognition module and converts it into text"""

    audio = take_user_input()

    try:
        query = recognize(audio).split()

        if BOTNAME.lower() in query:
            speak(choice(waiting))

            audio = take_user_input()

            try:
                query = recognize(audio)

                if "hello" in query or "hi" in query or "hey" in query:
                    speak("Hello %s" % (USERNAME))
                elif "what can you do" in query:
                    for i in range(len(commands)):
                        speak("Using %s in your command. I will %s" % (commands[i][0], commands[i][1]))
                elif "start my day" in query:
                    current_date = date()
                    news = get_latest_news()
                    weather, temperature, feels_like = get_weather_report("Toronto")

                    speak("Today is %s. It is currently %s, with a temperature of %s and it feels like %s. Today's top news is %s" % (current_date, weather, temperature, feels_like, news))
                elif "search" in query:
                    spell_word = query.find("search")

                    result = search_on_wikipedia(query[spell_word+len("search "):])
                    speak(result)
                elif "spell" in query:
                    spell_word = query.find("spell")

                    words = query[spell_word+len("spell "):]

                    speak(words)
                    for letter in words:
                        if letter == " ":
                            speak("space")
                        else:
                            speak(letter)
                elif "time" in query:
                    current_time = time()

                    speak("It is currently %s" % (current_time))
                elif "date" in query:
                    current_date = date()

                    speak("Today is %s" % (current_date))
                elif "youtube" in query:
                    speak("What video would you like to watch?")

                    audio = take_user_input()

                    try:
                        query = recognize(audio)

                        play_on_youtube(query)
                    except Exception:
                        speak(retry)
                        query = "None"
                    return query
                elif "news" in query:
                    news = get_latest_news()

                    speak(news)
                elif "weather" in query:
                    speak("Which city do you want to check the weather for?")

                    audio = take_user_input()

                    try:
                        query = recognize(audio)

                        weather, temperature, feels_like = get_weather_report(query)

                        speak("It is currently %s, with a temperature of %s and it feels like %s" % (weather, temperature, feels_like))
                    except Exception:
                        speak(retry)
                        query = "None"
                    return query
                elif "+" in query or "-" in query or "*" in query or "/" in query:
                    answer = calculation(query)

                    speak(answer)
                elif "thank you" in query or "thanks" in query:
                    speak(choice(thank_you_message))
                elif "goodbye" in query or "shut down" in query:
                    hour = datetime.now().hour

                    if "shut down" in query:
                        speak("shutting down")
                    elif hour >= 18:
                        speak("Good night sir, take care!")
                    else:
                        speak("Have a good day sir!")
                    exit()
                else:
                    speak("I currently cannot do that command")
            except Exception:
                speak(retry)
                query = "None"
            return query
    except Exception:
        query = "None"
    return query

if __name__ == "__main__":
    greet_user()

    #non-stop running the program until run() hits exit()
    while True:
        run()