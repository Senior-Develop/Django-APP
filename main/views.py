from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.utils.html import mark_safe
# from django.contrib.auth.forms import AuthenticationForm
# from cuser.forms import AuthenticationForm
from cuser.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.core.files.storage import FileSystemStorage, Storage
from zipfile import ZipFile
from django.conf import settings
import pandas as pd
import json, csv
import numpy as np
import requests
from datetime import datetime
import math
import os
from .models import Location, LocationHistory
# from .forms import NewUserForm, LocHistFileForm #from local forms.py file
from .forms import LocHistFileForm, HistUserForm  # from local forms.py file
import main.constants as const
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import random
import undetected_chromedriver.v2 as uc
from os.path import dirname, abspath
import os

BASE = os.path.dirname(abspath(__file__))
download = os.path.join(dirname(dirname(abspath(__file__))), "media/loc_hist")


def get_proxies():
    with open(os.path.join(BASE, "proxy.txt")) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    PROXIES = [x.strip() for x in content]

    return PROXIES


def proxy_driver(PROXIES):
    co = uc.ChromeOptions()
    co1 = uc.ChromeOptions()

    co.add_argument("--disable-extensions")
    co.add_argument("--disable-popup-blocking")
    # co.add_argument("--profile-directory=Default")
    co.add_argument("--disable-plugins-discovery")
    co.add_argument("--incognito")
    co.add_argument("--headless")
    co.add_argument('--no-sandbox')
    co.add_argument("--disable-setuid-sandbox")
    # co.add_argument("user_agent=DN")
    co.add_argument("--start-maximized")

    prefs = {"profile.default_content_settings.popups": 0,
             "download.default_directory": download,
             "directory_upgrade": True}
    co.add_experimental_option("prefs", prefs)
    co1.add_argument("--headless")

    pxy = random.choice(PROXIES)
    # pxy = "2.56.46.10:8800"

    co.add_argument('--proxy-server=%s' % pxy)
    uc_caps = co.to_capabilities()

    # driver = uc.Chrome(options=co)
    driver = uc.Chrome(options=co1, desired_capabilities=uc_caps)
    driver.delete_all_cookies()

    return driver


def download_google(driver, email, m_password, recovery_mail, recovery_phone):
    # google_url = "https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?redirect_uri=https%3A%2F" \
    # "%2Fdevelopers.google.com%2Foauthplayground&prompt=consent&response_type=code&client_id=407408718192" \
    # ".apps.googleusercontent.com&scope=email&access_type=offline&flowName=GeneralOAuthFlow"
    takeout_url = "https://takeout.google.com/"
    driver.get(takeout_url)
    delay = 5
    try:
        WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.ID, 'identifierId')))
        print("Page is ready!")

        # Enter google mail input
        try:
            input_mail = driver.find_element_by_id("identifierId")
            input_mail.clear()
            input_mail.send_keys(email)
            time.sleep(2)

            submit = driver.find_element_by_id("identifierNext")
            driver.execute_script("arguments[0].click();", submit)
            time.sleep(2)
        except:
            time.sleep(1)
            pass

        # Enter google password input
        try:
            time.sleep(4)
            input_password = driver.find_element_by_name("password")
            input_password.clear()
            input_password.send_keys(m_password)
            time.sleep(2)

            submit = driver.find_element_by_id("passwordNext")
            driver.execute_script("arguments[0].click();", submit)
            time.sleep(2)
        except:
            time.sleep(1)
            pass

        # Wrong Password
        try:
            time.sleep(2)
            driver.find_element_by_xpath(
                "//span[contains(text(), 'Wrong password. Try again or click ‘Forgot password’ to reset it.')]")
            time.sleep(1)
            return "Wrong password . Try again"
        except:
            time.sleep(1)
            pass

        # Google couldn't verify
        try:
            time.sleep(2)
            heading = driver.find_element_by_id("headingText").text
            if heading == "Couldn't sign you in":
                time.sleep(1)
                return "Google couldn't verify that this account. Try again another account"
        except:
            time.sleep(1)
            pass

        # check recovery mail
        try:
            time.sleep(2)
            recovery = driver.find_element_by_xpath("//*[contains(text(), 'Confirm your recovery email')]")
            driver.execute_script("arguments[0].click();", recovery)
            time.sleep(2)


        except Exception as e:
            time.sleep(1)
            # return "Wrong confirm mail: " + str(e)
            pass

        try:
            r_mail = driver.find_element_by_xpath("//input[@type='email']")
            r_mail.send_keys(recovery_mail)
            time.sleep(2)
            nextButton = driver.find_element_by_xpath(
                '//*[@id="view_container"]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button')
            driver.execute_script("arguments[0].click();", nextButton)
            time.sleep(2)
        except:
            time.sleep(1)
            pass

        # check recovery phone number
        try:
            time.sleep(2)
            recovery_p = driver.find_element_by_xpath("//*[contains(text(), 'Confirm your recovery phone number')]")
            driver.execute_script("arguments[0].click();", recovery_p)
            time.sleep(2)


        except Exception as e:
            time.sleep(1)
            # return "Wrong confirm phone: " + str(e)
            pass

        try:
            r_phone = driver.find_element_by_id("phoneNumberId")
            r_phone.send_keys(recovery_phone)
            time.sleep(2)
            nextButton = driver.find_element_by_xpath(
                '//*[@id="view_container"]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button')
            driver.execute_script("arguments[0].click();", nextButton)
            time.sleep(2)
        except:
            time.sleep(1)
            pass

        # Press confirm button
        try:

            confirm_button = driver.find_element_by_xpath("//i[contains(text(), 'Confirm')]")
            driver.execute_script("arguments[0].click();", confirm_button)
            time.sleep(2)

        except:
            time.sleep(1)
            pass

        # download file page deselect all and select location info check box
        try:
            # driver.get(takeout_url)
            button_deselect = driver.find_element_by_xpath("//button[@aria-label='Deselect all']")
            driver.execute_script("arguments[0].click();", button_deselect)
            time.sleep(2)

            g_location = driver.find_element_by_name("Maps (your places)")
            driver.execute_script("arguments[0].click();", g_location)
            time.sleep(2)

            next_step = driver.find_element_by_xpath("//button[@aria-label='Next step']")
            driver.execute_script("arguments[0].click();", next_step)
            time.sleep(2)
        except Exception as e:
            time.sleep(1)
            return "download failed" + str(e)

        # create export button click
        try:
            export_button = driver.find_element_by_xpath("//span[contains(text(), 'Create export')]")
            driver.execute_script("arguments[0].click();", export_button)
            time.sleep(2)

        except:
            time.sleep(1)
            pass

        # manage your export page ... find element download div
        try:
            time.sleep(10)
            # driver.get("https://takeout.google.com/takeout/downloads")
            # time.sleep(5)
            download_bodys = driver.find_elements_by_tag_name("tbody")
            for d_body in download_bodys:
                target = d_body.find_element_by_xpath("//i[contains(text(), 'file_download')]")
                if target:
                    download_button = driver.find_element_by_xpath("//a[@aria-label='Download']")
                    driver.execute_script("arguments[0].click();", download_button)
                    time.sleep(2)
                    return "download file success"
        except:
            time.sleep(1)
            pass

        # Again enter google password input
        try:

            input_password = driver.find_element_by_name("password")
            input_password.clear()
            input_password.send_keys(m_password)
            time.sleep(2)

            submit = driver.find_element_by_id("passwordNext")
            driver.execute_script("arguments[0].click();", submit)
            time.sleep(2)
        except:
            time.sleep(1)
            pass

    except TimeoutException:
        print("Page Loading took too much time!")


# Create your views here.
def homepage(request):
    #    return HttpResponse("Wow, the homepage is working")
    return render(request=request,
                  template_name="main/home.html",
                  context={"locations": Location.objects.all})


def logout_request(request):
    logout(request)
    messages.info(request, "Logged out")
    return redirect("main:homepage")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        #        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()  # the user is created
            email = form.cleaned_data.get('email')
            messages.success(request, f"New Account Created: {email}")
            # this just creates the message - will need to be retrieved - then they are gone
            # request insures it goes to this specific user
            messages.info(request, f"You are now loged in as {email}")
            login(request, user)  # user is loged in
            return redirect("main:homepage")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

    form = UserCreationForm
    #    form = NewUserForm
    return render(request,
                  "main/register.html",
                  context={"form": form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            #            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            #            user = authenticate(username=username, password=password)
            user = authenticate(email=email, password=password)
            messages.info(request, f"authenticate: un:{email} p:{password} u:{user}")

            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {email}")
                return redirect("main:homepage")
            else:
                messages.error(request, "Invalid email or password")
        else:
            messages.error(request, "Invalid email or password")

    form = AuthenticationForm()
    return render(request,
                  "main/login.html",
                  {"form": form})


def upload(request):
    if request.method == 'POST':
        form = LocHistFileForm(request.POST, request.FILES)
        # user = request.user
        # messages.error(request, f"user: {user}")
        # form.user = user

        if form.is_valid():
            upfile = request.FILES['zip_file']

            try:
                with ZipFile(upfile, 'r') as zip:
                    zip_members = zip.namelist()

            except:
                messages.error(request, f"Error opening file")

            else:
                sem_members = [i for i in zip_members
                               if (('Semantic Location History/' in i) & ('.json' in i))]
                messages.error(request, f"sem_members: {sem_members}")
                points_members = [i for i in zip_members if 'Location History.json' in i]
                messages.error(request, f"points_members: {points_members[0]}")

                if not sem_members or not points_members:
                    messages.warning(request, f"Location History data not found in file")
                else:

                    locHist = form.save(commit=False)

                    if (request.user.is_authenticated):
                        locHist.user = request.user
                    else:
                        if not request.session.exists(request.session.session_key):
                            request.session.create()
                        locHist.session_key = request.session.session_key

                    #                        locHist.session = Session.objects.get(session_key=request.session.session_key)

                    #                        if not request.session.exists(request.session.session_key):
                    #                            request.session.create()
                    #                        locHist.session = request.session.session_key

                    messages.error(request, f"user auth: {request.user.is_authenticated}")
                    messages.error(request, f"session_key {request.session.session_key}")

                    locHist.save()

                    dirName = os.path.splitext(locHist.zip_file.path)[0]
                    messages.error(request, f"dirName path {dirName}")

                    try:
                        os.mkdir(dirName)
                    except OSError as error:
                        messages.error(request, error)
                        print(error)

                    locHist.dir = dirName
                    locHist.sem_dir = os.path.join(locHist.dir, 'Takeout/Location History/Semantic Location History/')
                    locHist.point_file = os.path.join(locHist.dir, 'Takeout/Location History/Location History.json')
                    locHist.save()

                    try:
                        with ZipFile(upfile, 'r') as zip:
                            for m in sem_members:
                                zip.extract(member=m, path=dirName)

                            zip.extract(member=points_members[0], path=dirName)
                            messages.error(request, "extract complete")

                    except OSError as error:
                        messages.error(request, f"Error opening extractng zip file")
                        messages.error(request, error)

                    return redirect("main:homepage")

        else:
            messages.error(request, f"path4: {request.FILES}")

            for field, items in form.errors.items():
                for item in items:
                    messages.error(request, '{}: {}'.format(field, item))

    else:
        form = LocHistFileForm()

    return render(request, "main/upload.html", {'form': form})


def freqloc(request):
    # return HttpResponse("Wow, freqloc is working")

    locHist = {}

    if (request.user.is_authenticated):
        #        locHist.user = request.user
        try:
            locHist = LocationHistory.objects.filter(user=request.user).latest("uploaded_at")
        except:
            messages.error(request, 'Your location data could not be found.  Please upload below.')
            return redirect("main:upload")
    else:
        if not request.session.exists(request.session.session_key):
            request.session.create()
        #        locHist.session_key = request.session.session_key
        try:
            locHist = LocationHistory.objects.filter(session_key=request.session.session_key).latest("uploaded_at")
        except:
            messages.error(request, mark_safe(
                "Your location data could not be found.  Please <a href='../login/'>log into your account</a> or "
                "upload below."))
            return redirect("main:upload")

    messages.error(request, f"Session: {request.session.session_key}")
    messages.error(request, f"LocHist: {locHist.point_file}")

    #    with open('Location History Josh DL 2020-05.json', 'r') as f:
    # with open( userLocDir + locDir + locFile , 'r') as f: #from google takeout folders

    with open(locHist.point_file, 'r') as f:
        locHistDict = json.load(f)

    #    [data_days_c, time_frame_days_c, dfp] = locHistDictToDF(locHist)
    [data_days_c, dfp] = locHist.locHistDictToDF(locHistDict)

    messages.error(request, f"data_days_c: {data_days_c}")

    return render(request=request,
                  template_name="main/home.html",
                  context={"locations": Location.objects.all})


def google_takeout_login(request):
    if request.method == "POST":
        form = HistUserForm(request.POST)
        if form.is_valid():
            #            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            recovery_mail = form.cleaned_data.get('recovery_mail')
            recovery_phone = form.cleaned_data.get('recovery_phone')
            #            user = authenticate(username=username, password=password)
            #            user = authenticate(email=email, password=password)
            messages.info(request, f"authenticate: un:{email} p:{password}")

            ALL_PROXIES = get_proxies()
            # --- YOU ONLY NEED TO CARE FROM THIS LINE ---
            # creating new driver to use proxy
            driver = proxy_driver(ALL_PROXIES)

            try:
                result_message = download_google(driver, email, password, recovery_mail, recovery_phone)
                time.sleep(5)
                messages.info(request, result_message)
                driver.close()
            except:
                print("download failed")
                time.sleep(5)
                driver.close()
                pass

        else:
            messages.error(request, "Invalid email or password")
    #
    form = HistUserForm()
    return render(request,
                  "main/google_takeout_login.html",
                  {"form": form})
