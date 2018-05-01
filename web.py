# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 13:37:07 2018

@author: shadowleaf
"""

import sched
import time
import threading

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

"""# create a new Firefox session)
driver = webdriver.Firefox()
driver.implicitly_wait(60)
driver.maximize_window()"""

# using the chrome driver
chromedriver_location = "C:\Users\shadowleaf\Anaconda2\selenium\webdriver\chrome\chromedriver.exe"
chrome_options = webdriver.ChromeOptions()
# save the sessions for reuse
chrome_options.add_argument("user-data-dir=selenium")
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chromedriver_location)

incoming_scheduler = sched.scheduler(time.time, time.sleep)
last_printed_msg = None
last_thread_name = ''

# Navigate to the web-whatsapp
driver.get("https://web.whatsapp.com")
time.sleep(10)

# send a message
def send_message(driver, message):
    input_box = driver.find_element(By.XPATH, '//*[@id="main"]//footer//div[contains(@contenteditable, "true")]')
    input_box.click()
    action = ActionChains(driver)
    action.send_keys(message)
    action.send_keys(Keys.RETURN)
    action.perform()

# get messages after every interval amount of time
def message_scheduling(driver):
    incoming_scheduler.enter(5, 1, get_message, (driver, incoming_scheduler))
    incoming_scheduler.run()

# get messages
def get_message(driver, scheduler):
    global last_printed_msg
    try:
        all_messages = driver.find_elements(By.XPATH, '//*[@id="main"]//div[contains(@class, "message")]')
        # check if there is atleast one message in the chat, mostly this will be true
        if len(all_messages) >= 1:
            last_msg_sender, last_msg_text = get_msg_info(all_messages[-1])
            msg_new = True
        else:
            msg_new = False
        
    except Exception as e:
        print(e)
        msg_new = False
    
    if msg_new :
        if last_printed_msg == last_msg_sender + last_msg_text:
            pass
        else:
            msg_to_print = []
            for i, curr_message in reversed(list(enumerate(all_messages))):
                curr_msg_sender, curr_msg_text = get_msg_info(curr_message)
                if last_printed_msg == curr_msg_sender + curr_msg_text:
                    break
                else:
                    msg_to_print.append([curr_msg_sender, curr_msg_text])
                    
            for msg_sender, msg_text in reversed(msg_to_print):
                print msg_sender, " : ", msg_text
                last_printed_msg = msg_sender + msg_text
    
    incoming_scheduler.enter(5, 1, get_message, (driver, scheduler, ))

# get the message info
def get_msg_info(webdriver_element):
    try:
        msg = webdriver_element.find_element(By.XPATH,'.//div[contains(@class, "copyable-text")]')
        msg_sender = msg.get_attribute('data-pre-plain-text')
        msg_text = msg.find_elements(By.XPATH, './/span[contains(@class, "selectable-text")]')[-1].text
    except IndexError:
        msg_text = ""
    except Exception:
        msg_text = ""
        msg_sender = ""
    
    return msg_sender, msg_text
    
def choose_receiver(driver, receiver):
    input_box = driver.find_element(By.XPATH, '//*[@id="side"]//input')
    input_box.clear()
    input_box.click()
    input_box.send_keys(receiver)
    input_box.send_keys(Keys.RETURN)
    print_thread_name(driver)

def print_thread_name(driver):
    global last_thread_name
    try:    
        curr_thread_name = driver.find_element(By.XPATH, '//*[@id="main"]/header//span[contains(@dir, "auto")]').text
    except Exception as e:
        curr_thread_name = "No Thread Selected"
        print(e)
    if curr_thread_name != last_thread_name:
        last_thread_name = curr_thread_name
        print "Now sending messages to : ", curr_thread_name
    return curr_thread_name

def get_contacts(driver):
    button = driver.find_element(By.XPATH, '//*[@id="side"]//div[contains(@title, "New chat")]')
    button.click()

def main():
    global last_thread_name
    # getting true name of contact/group
    last_thread_name = driver.find_element(By.XPATH, '//*[@id="main"]/header//span[contains(@dir, "auto")]').text
    
    # start background threading
    incoming_thread = threading.Thread(target=message_scheduling, args=(driver,))
    incoming_thread.start()
    receiver = raw_input("Enter the Receiver's name : ")
    choose_receiver(driver, receiver)
    while True:
        msg_to_send = raw_input("Enter the Message to send : ")
        send_message(driver, msg_to_send)
        if_exit = raw_input("Exit ? (y/n) : ")
        if if_exit == "y":
            break
        
if __name__=='__main__':
    main()

# close the browser window
driver.quit()