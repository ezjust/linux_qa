from virtualbox import Virtualbox
from system import Executor
import traceback
import os
import selenium
import subprocess
import ConfigParser
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.common.exceptions import *
from bs4 import BeautifulSoup
import time
import re
import urllib
import datetime
import sys
# driver.implicitly_wait(10) # seconds

work_path = os.path.abspath('.') + '/'  # Returns current directory, where script is run.
config = work_path + "config.ini"



def read_cfg():
    cp = ConfigParser.ConfigParser()
    cp.readfp(open(config))
    ip_machine = cp.get('web', 'ip')
    username_machine = cp.get('web', 'username_machine')
    password_machine = cp.get('web', 'password_machine')
    ip_livecd = cp.get('web', 'ip_livecd')
    pass_livecd = cp.get('web', 'pass_livecd')
    vbox_vmname = cp.get('web', 'vbox_livedvdname')
    vbox_export_vmname = cp.get('web', 'vbox_export_vmname')
    core_ip = cp.get('general', 'core_ip')
    core_login = cp.get('general', 'core_login')
    core_password = cp.get('general', 'core_password')
    core_link = 'https://' + core_ip + ':8006/apprecovery/admin'
    protect_agent = cp.get('web', 'protect_agent')
    build_agent = cp.get('general', 'build_agent')
    rollback_agent = cp.get('web', 'rollback_agent')
    auto_bmr_agent = cp.get('web', 'auto_bmr_agent')
    bmr_bootable_agent = cp.get('web', 'bmr_bootable_agent')
    force_snapshot_agent = cp.get('web', 'force_snapshot_agent')
    return ip_machine, username_machine, password_machine, ip_livecd, core_ip, core_login, core_password, pass_livecd, vbox_vmname, core_link, protect_agent, build_agent, rollback_agent, auto_bmr_agent, bmr_bootable_agent, force_snapshot_agent, vbox_export_vmname


ip_machine, username_machine, password_machine, ip_livecd, core_ip, core_login, core_password, pass_livecd, vbox_vmname, core_link, protect_agent, build_agent, rollback_agent, auto_bmr_agent, bmr_bootable_agent, force_snapshot_agent, vbox_export_vmname = read_cfg()


class WebAgent(object):
    short_timeout = 60
    long_timeout = 200
    agent_link = None
    id_agent = None

    virtualbox = Virtualbox()
    execute = Executor()

    def __init__(self):
        try:
            self.driver = webdriver.Firefox()
            try:
                self.driver.set_page_load_timeout(30) #stopped work in the newest firefox. Before was ok.
            except WebDriverException:
                time.sleep(5)
                pass
            #self.driver.implicitly_wait(30)
            self.driver.accept_untrusted_certs = True
            self.driver.assume_untrusted_cert_issuer = True
            self.driver.get(core_link)
            # self.driver.refresh()
        except Exception:
            print Exception

    def open_core_ui(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.alert_is_present())
            asd = self.driver.switch_to_alert()
            asd.send_keys(core_login)
            asd.send_keys(Keys.TAB + core_password)
            asd.accept()
            print("Core UI is open")
            if self.driver.current_url is not core_link:
                print(self.driver.current_url)
                time.sleep(5)
            # time.sleep(2)
            # self.driver.refresh()

        except TimeoutException:
            self.driver.close()

    def wait_for_element_invisible(self, element_id):
        try:
            WebDriverWait(self.driver, self.short_timeout).until(
                EC.presence_of_element_located((By.ID, element_id)))
            WebDriverWait(self.driver, self.long_timeout).until(
                EC.invisibility_of_element_located((By.ID, element_id)))
        except TimeoutException:
            pass

    def find_machine_link(self, ip_machine):
        self.ip_machine = ip_machine
        WebDriverWait(self.driver, self.long_timeout, ignored_exceptions=['selenium.common.exceptions.StaleElementReferenceException']).until(
            EC.presence_of_element_located((By.TAG_NAME, 'a')))
        time.sleep(5)
        set_of_machine = self.driver.find_element(By.ID,
                                                  "apgProtected"). \
            find_element(By.CLASS_NAME, "ui-agents-panel-content")
        for elem in set_of_machine.find_elements_by_tag_name('a'):
            # try:
            #     print elem.get_attribute('href')
            # except selenium.common.exceptions.StaleElementReferenceException as e:
            #     # print len(set_of_machine)
            #     print "MY ERROR", e
                # test = None
            try:
                test = elem.get_attribute('href')
                # print "ELEM", elem.text
                # print "SELF IP", self.ip
                if elem.text in [self.ip_machine]:
                    self.agent_link = test
                    self.id_agent = re.split(r'Machines/*', self.agent_link)[1]
                    # print "AGENT LINK", self.agent_link
                    return self.agent_link
            except Exception:
                continue
            # print("self.ip  is up")
    #
    # def find_machine_link2(self):
    #     print("I am in find machine link")
    #     WebDriverWait(self.driver, self.long_timeout).until(
    #         EC.presence_of_element_located((By.TAG_NAME, 'a')))
    #     try:
    #         set_of_machine = self.driver.find_element(By.ID,
    #                                                   "apgProtected").find_elements_by_tag_name(
    #             'a')
    #         # print set_of_machine
    #         for elem in set_of_machine:
    #
    #             test = elem.get_attribute('href')
    #             # print test
    #             # print elem.text
    #             # print(self.ip)
    #             # print("self.ip  is up")
    #             if elem.text in self.ip_machine:
    #                 self.agent_link = test
    #                 self.id_agent = re.split('Machines/*', self.agent_link)[1]
    #                 # print(self.agent_link)
    #                 return (self.agent_link)
    #     except StaleElementReferenceException:
    #         pass

    def find_last_job_id(self):

        """We are looking in events the last one job_id. This job_id we can use is compare with the current one job id, to make sure, that we parse the status of the appropriate job.
        Here is output of the this job id : 405bf1d0-e552-4b3f-8dc6-f8a4f2310d8f
        """
        try:
            self.last_job_attr = self.list_events(ip_machine)

        except IndexError:
            self.last_job_attr = 'null'

        return self.last_job_attr





    def protect_new_agent(self, ip_machine, username, password):

        self.ip_machine = ip_machine
        self.username = username
        self.password = password
        agent_link = None
        id = None


        try:
            print(datetime.datetime.now().time())
            print("I am starting to protect agent %s, %s, %s" % (self.ip_machine, self.username, self.password))
            # print("here")
            if build_agent == '7.1.0':
                try:
                    WebDriverWait(self.driver, self.short_timeout).until(
                EC.element_to_be_clickable((By.XPATH, ".//*[@id='protectMachine']/a[1]")))
                    new = self.driver.find_element_by_xpath(".//*[@id='protectMachine']/a[1]")
                except WebDriverException:
                    time.sleep(5)
                    WebDriverWait(self.driver, self.short_timeout).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, ".//*[@id='protectMachine']/a[1]")))
                    new = self.driver.find_element_by_xpath(
                        ".//*[@id='protectMachine']/a[1]")
            else:
                print('7.0.0')
                print('test')
                try:
                    WebDriverWait(self.driver, self.short_timeout).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, ".//*[@id='protectMachine']/a[1]/span")))
                    new = self.driver.find_element_by_xpath(
                        ".//*[@id='protectMachine']/a[1]/span")
                    while new.text not in "Protect":
                        WebDriverWait(self.driver, self.short_timeout).until(
                            EC.element_to_be_clickable(
                                (
                                By.XPATH, ".//*[@id='protectMachine']/a[1]/span")))
                        new = self.driver.find_element_by_xpath(
                            ".//*[@id='protectMachine']/a[1]/span")
                except WebDriverException:
                    time.sleep(5)
                    WebDriverWait(self.driver, self.short_timeout).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, ".//*[@id='protectMachine']/a[1]/span")))
                    new = self.driver.find_element_by_xpath(
                    ".//*[@id='protectMachine']/a[1]/span")
                    while new.text not in "Protect":
                        WebDriverWait(self.driver, self.short_timeout).until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                ".//*[@id='protectMachine']/a[1]/span")))
                        new = self.driver.find_element_by_xpath(
                        ".//*[@id='protectMachine']/a[1]/span")
            #time.sleep(5)
            #WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable(new))
            new.click()
            print("here2")
            WebDriverWait(self.driver, self.long_timeout).until(EC.text_to_be_present_in_element((By.CLASS_NAME, "wizard-header-info"), "The Protect Machine wizard helps you to quickly and easily protect a machine."))
            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='btnWizardDefault']")))
            next = self.driver.find_element_by_xpath(".//*[@id='btnWizardDefault']")
            next.click()

            WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.XPATH, ".//*[@id='hostName']")))

            hostname = self.driver.find_element_by_xpath(".//*[@id='hostName']")
            hostname.send_keys(self.ip_machine)

            usernm = self.driver.find_element_by_xpath(".//*[@id='userName']")
            usernm.send_keys(self.username)

            passwd = self.driver.find_element_by_xpath(".//*[@id='password']")
            passwd.send_keys(self.password)

            next = self.driver.find_element_by_xpath(".//*[@id='btnWizardDefault']")
            next.click()
            print(datetime.datetime.now().time())
            self.wait_for_element_invisible(element_id="lpLoadingContent")
            print(datetime.datetime.now().time())

            # WebDriverWait(self.driver, self.short_timeout).until(EC.visibility_of_element_located((By.XPATH, ".//*[@id='btnWizardDefault']"))) # this part should be rechecked. Since, there is bug.

            # WebDriverWait(self.driver, self.short_timeout).until(
            #     EC.presence_of_element_located((By.XPATH, ".//*[@id='wizardContentContainer']/div[2]/div[2]/div/div[1]/div/label/span/text()")))
            upgrade = self.driver.find_element_by_id("wizardContentContainer")
            if upgrade is not None:
                #print upgrade.text
                if "The target machine is running an older version of the Quest Rapid Recovery Agent software" in upgrade.text:
                    click_upgrade = self.driver.find_element_by_id("upgradeAgent")
                    click_upgrade.click()

                    print("I was in upgrade section and considered that machine is suitable for upgrade")
                    #print(upgrade.text)
                    next_button = self.driver.find_element_by_id("btnWizardDefault")
                    next_button.click()
            #print(datetime.datetime.now().time())

            time.sleep(2)
            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.ID, "btnWizardBack")))
            back = self.driver.find_element_by_xpath(".//*[@id='btnWizardBack']")
            back.click()
            #print(datetime.datetime.now().time())

            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='btnWizardDefault']")))
            next = self.driver.find_element_by_xpath(".//*[@id='btnWizardDefault']")
            next.click()
            #print(datetime.datetime.now().time())

            #print("Before")
            WebDriverWait(self.driver, self.short_timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, "control-label")))
            check = self.driver.find_element_by_class_name('control-label')
            if check.text is not None:
                counter = 0
                try:
                    text = check.text
                    while "Display name:" not in text and counter < 60:
                        #print("--------------------------------")
                        counter = counter + 1
                        #print("Waiting for Display name:")
                       # print(text)
                        time.sleep(5)
                        WebDriverWait(self.driver, self.short_timeout).until(
                            EC.visibility_of_element_located(
                                (By.CLASS_NAME, "control-label")))
                        check = self.driver.find_element_by_class_name(
                            'control-label')
                        text = check.text
                        #print("===============================")


                    #print("checktest is: ")
                    #print(check.text)

                    if "Display name:" in check.text:
                        WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='btnWizardDefault']")))
                        finish = self.driver.find_element_by_xpath(".//*[@id='btnWizardDefault']")
                        finish.click()
                        #print(datetime.datetime.now().time())
                        #print("After")
                    else:
                        raise Exception("TIMEOUT IN THE PROTECTION WIZARD")

                finally:
                    pass

            self.wait_for_element_invisible(element_id="lpLoadingContent")
            #print(datetime.datetime.now().time())

            print("The agent %s with the credentials: %s and %s is protected" % (self.ip_machine, self.username, self.password))

            counter = 0
            while self.find_machine_link(self.ip_machine) is None and counter < 60:
                print("waiting protected machine to appear")
                time.sleep(5)
                counter = counter + 1

            #print("asd")
            try:
                self.driver.get(str(self.agent_link))
                time.sleep(2)
            except TimeoutException:
                time.sleep(10)
                print(self.driver.current_url)
                print(self.agent_link)
            finally:
                if self.driver.current_url != self.agent_link:
                    x = 0
                    self.driver.get(str(self.agent_link))
                    while self.driver.current_url != self.agent_link and x < 12:
                        x = x + 1
                        time.sleep(10)
                        print('waiting agent link to appear')
                    if self.driver.current_url != self.agent_link:
                        print("They are differ")
                        raise Exception

            #print(datetime.datetime.now().time())

            print("Machine is protected. New transfer will be started")
            #print(datetime.datetime.now().time())

            self.find_last_job_id()
            #print(datetime.datetime.now().time())

            if self.driver.current_url != self.agent_link:
                self.driver.get(str(self.agent_link))
                time.sleep(10)

            WebDriverWait(self.driver, self.long_timeout).until(EC.element_to_be_clickable((By.XPATH ,".//*[@id='volumesGroupsGrid_selectAll_triSpan']")))
            all_volumes = self.driver.find_element_by_xpath(".//*[@id='volumesGroupsGrid_selectAll_triSpan']")
            all_volumes.click()

            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.ID, "setScheduleForAgent")))
            schedule = self.driver.find_element_by_id("setScheduleForAgent")
            schedule.click()
            WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.XPATH, ".//*[@id='weekdaysPeriod']")))
            every = self.driver.find_element_by_xpath(".//*[@id='weekdaysPeriod']")
            every.send_keys(Keys.LEFT_CONTROL, "a")
            every.send_keys(Keys.DELETE)
            every.send_keys("40")
            # WebDriverWait(self.driver, self.short_timeout).until(EC.visibility_of_element_located((By.XPATH, ".//*[@id='content']/div[2]/div[2]/div[1]/span")))
            apply = self.driver.find_element_by_id("protectionScheduleEditOK")
            apply.click()

            print("Schedule is configured")
            #print("HERE1")
            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='machineDetailesToolbar_" + self.id_agent + "']/ul/li[6]/a/span")))
            force_snapshot = self.driver.find_element_by_xpath(".//*[@id='machineDetailesToolbar_" + self.id_agent + "']/ul/li[6]/a/span")
            force_snapshot.click()
            #print("HERE2")
            self.wait_for_element_invisible(element_id="lpLoadingContent")
            #print("HERE3")
            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='machineDetailesToolbar_" + self.id_agent + "']/ul/li[6]/a")))
            first_force = self.driver.find_element_by_xpath(".//*[@id='machineDetailesToolbar_" + self.id_agent + "']/ul/li[6]/a")
            first_force.click()
            #print("HERE4")
            self.wait_for_element_invisible(element_id="lpLoadingContent")
            self.driver.find_element_by_class_name("btn-container").send_keys(Keys.ENTER)
            self.wait_for_element_invisible(element_id="lpLoadingContent")
            #print("HERE5")

        except Exception:
            print("HERE")
            print Exception
            raise Exception


        finally:
            print('Finaly')
            pass

    def force_snapshot(self, ip_machine, base):

        self.ip = ip_machine
        self.base = base
        agent_link = None
        id = None


        try:
            while self.find_machine_link(self.ip) is None:
                print(self.find_machine_link(self.ip))
                print("waiting protected machine to appear")
                time.sleep(5)
            print("Going to start new snapshot.")

            self.driver.get(str(self.agent_link))

            self.find_last_job_id()

            if self.driver.current_url != self.agent_link:
                self.driver.get(str(self.agent_link))
                time.sleep(10)

            # print("HERE1")
            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='machineDetailesToolbar_" + self.id_agent + "']/ul/li[6]/a/span")))
            force_snapshot = self.driver.find_element_by_xpath(".//*[@id='machineDetailesToolbar_" + self.id_agent + "']/ul/li[6]/a/span")
            force_snapshot.click()
            # print("HERE2")
            self.wait_for_element_invisible(element_id="lpLoadingContent")
            # print("HERE3")

            #default ( First time is base, all other should be incremental )
            if self.base == False:
                print("Incremental snapshot is starting...")
                WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='popup1']/div/div[6]/form/div[2]/button[3]")))
                force_snapshot_default = self.driver.find_element_by_xpath(".//*[@id='popup1']/div/div[6]/form/div[2]/button[3]")
                force_snapshot_default.click()
            else:
                print("Base snapshot is starting...")
                WebDriverWait(self.driver, self.short_timeout).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, ".//*[@id='popup1']/div/div[6]/form/div[2]/button[2]")))
                force_base_image = self.driver.find_element_by_xpath(
                    ".//*[@id='popup1']/div/div[6]/form/div[2]/button[2]")
                force_base_image.click()
                # print("HERE4")
                self.wait_for_element_invisible(element_id="lpLoadingContent")
                self.driver.find_element_by_class_name("btn-container").send_keys(Keys.ENTER)

            self.wait_for_element_invisible(element_id="lpLoadingContent")
            # print("HERE5")


        finally:
            pass




    def remove_agent_by_id(self, ip_machine):


        self.ip = ip_machine
        not_protected = None

        try:

            self.find_machine_link(self.ip)
            counter = 0
            while self.agent_link == None:
                time.sleep(2.5)
                self.find_machine_link(self.ip)
                print("I got 'None' for the agent_link, 'timeout in 60 sec' is applied.")
                counter = counter + 1
                if counter == 12 :
                    not_protected = True
                    print("There was not found machine for remove.")
                    return
            try:
                self.driver.get(str(self.agent_link))

            except TimeoutException:
                time.sleep(5)
                self.driver.get(str(self.agent_link))


            finally:

                if self.driver.current_url != self.agent_link:
                    print self.driver.current_url
                    print self.agent_link
                    print Exception

            self.find_last_job_id()

            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='machineDetailesToolbar_" + self.id_agent + "']/ul/li[10]/a")))
            remove_agent = self.driver.find_element_by_xpath(".//*[@id='machineDetailesToolbar_" + self.id_agent + "']/ul/li[10]/a")
            remove_agent.click()
            time.sleep(2)
            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='DeleteRecoveryPoints']")))
            click_remove_with_recovery_points = self.driver.find_element_by_xpath(".//*[@id='DeleteRecoveryPoints']")
            click_remove_with_recovery_points.click()

            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='btnRemoveProtection']")))
            click_remove_default = self.driver.find_element_by_xpath(".//*[@id='btnRemoveProtection']")
            click_remove_default.click()


        finally:
            print('Remove RPs')
            '''Wait in self.status while all RPs are removed from the agent.
                        Return the status of this task'''
            # if not_protected is None:
            #     self.core_status(ip_machine)
            print("The agent removed")
            pass

    def list_events(self, ip_machine):
        self.ip = ip_machine
        agent_link = None
        self.status_of_the_job = None
        job_status = None
        job_name = None

        # try:
        #     self.find_machine_link(self.ip)
        #     while self.agent_link == None:
        #         time.sleep(5)
        #         self.find_machine_link(self.ip)
        #         print("I got None for agent_link, while is applied.")
        # except OSError as e:
        #     raise Exception("Here is bug in status with the agent link.")
        #
        # WebDriverWait(self.driver, self.short_timeout).until(
        #     EC.presence_of_element_located((By.TAG_NAME, 'a')))
        counter = 0
        while agent_link is None and counter < 10:
            try:
                set_of_machine = self.driver.find_element(By.ID,
                                                          "apgProtected").find_elements_by_tag_name(
                    'a')
                for elem in set_of_machine:
                    test = elem.get_attribute('href')
                    if elem.text in self.ip:
                        agent_link = test

                        # id = re.split('Machines/*', agent_link)[1]
                        # print("AGENT LINK", agent_link)

            except StaleElementReferenceException:
                pass
            time.sleep(12)
            counter = counter + 1

        if agent_link is None:
            print('agent_link is None')

        if self.driver.current_url != str(agent_link + "/Events"):
            self.driver.get(str(agent_link + "/Events"))
        if self.driver.current_url != str(agent_link + "/Events"):
            time.sleep(5)

        WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.ID, "cancelJobs")))
        # WebDriverWait(self.driver, 5).until(
        #     EC.invisibility_of_element_located((By.ID, "cancelJobs")))
        # element = self.driver.find_element_by_id('cancelJobs')
        #
        # while element.is_enabled() is True:
        #     print("Element is active")
        #     print(element.is_enabled())
        #     print(element.is_displayed())
        #     print(element.is_selected())
        time.sleep(2)
        #print('Gather list of events')
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        #print(
        #"--------------------------------------------------------------------------")
        substring = soup.find_all("tr", {"id": True})
        text = re.findall('id=".*?"', str(substring))
        list_id = []
        #print("asdasdasdasd")
        #print(list_id)
        #print("asdasdasdasd")
        for i in range(0, len(text) - 1):
            if len(text[i]) == int(41):
                if text[i][4:40] not in list_id:
                    list_id.append(text[i][4:40])

        #print(list_id)
        #print(
        #"--------------------------------------------------------------------------")
        #print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
        #print(list_id[0])
        substring = soup.find_all("tr", {"id": list_id[0]})
        #print(substring)
        #print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzsd')
        value = re.findall('value=".*?"', str(substring))
        value = value[2].split(" ", 1)
        value = value[0].split('value="', 1)[1]
        #print(value)
        title = re.findall('title=".*?"', str(substring))
        title = title[0].split('"', 1)
        title = title[1][0:(len(title[1]) - 1)]
        if len(title) > 20:
            title = "In Progress"
        #print(title)

        stat = {}

        def instert(id, value, result, dict):
            if not id in dict:
                dict[id] = [value, result]
            else:
                dict[id].append([value, result])

        for i in range(0, len(list_id)):
            substring = soup.find_all("tr", {"id": list_id[i]})
            #print(list_id[i])
            value = re.findall('value=".*?"', str(substring))
            #print(value)
            value = value[2].split(" ", 1)
            value = value[0].split('value="', 1)[1]

            if value is '"':
                value = re.findall('value=".*?"', str(substring))
                value = value[1].split(" ", 1)
                value = value[0].split('value="', 1)[1]

            # print(value)
            title = re.findall('title=".*?"', str(substring))
            # print title
            # print('134')
            if build_agent == '7.0.0':
                # print "Build agent is 7.0.0"
                title = title[0].split('"', 1)                                 #7.0.0 title: ['title=', 'Succeeded"']
                                                                               #7.1.0 title: ['Succeeded', '']

                # print("7.0.0 title: %s" % title)
                # print("7.1.0 title: %s" % title[1].split('"', 1))
            else:
                # print "Build agent is 7.1.0"
                title = title[1].split('"', 1)   # was title[0] before. Is not working now.
                                             # Fix is tested on the 7.1.0

            # print title
            #print('2')
            title = title[1][0:(len(title[1]) - 1)]
            #print title
            #print('3')
            if len(title) > 20:
                # print("I am here")
                if " of " in title:
                    # print("Gottcha")
                    title = "In Progress"
            #print(title)
            instert(id=list_id[i], value=value, result=title, dict=stat)

        # print(stat)
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(stat)
        #print("list_events_completed")
        return stat

    def core_events(self, ip_machine):
        self.ip = ip_machine

        agent_link = None
        self.status_of_the_job = None
        job_status = None
        job_name = None


        core_event_link = core_link + "/Core/Events"
        self.driver.get(core_event_link)
        while str(self.driver.current_url) != str(core_event_link):
            time.sleep(5)
            print('3')
            print(self.driver.current_url)
            print(core_event_link)

        WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.ID, "taskGrid")))
        time.sleep(3)


        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        # print(
        # "--------------------------------------------------------------------------")
        substring = soup.find_all("tr", {"id": True})
        text = re.findall('id=".*?"', str(substring))
        list_id = []
        # print("asdasdasdasd")
        # print(list_id)
        # print("asdasdasdasd")
        for i in range(0, len(text) - 1):
            if len(text[i]) == int(41):
                if text[i][4:40] not in list_id:
                    list_id.append(text[i][4:40])

        # print(list_id)
        # print(
        # "--------------------------------------------------------------------------")
        # print(list_id[0])
        substring = soup.find_all("tr", {"id": list_id[0]})
        # print(substring)
        value = re.findall('value=".*?"', str(substring))
        value = value[2].split(" ", 1)
        value = value[0].split('value="', 1)[1]
        # print(value)
        title = re.findall('title=".*?"', str(substring))
        title = title[0].split('"', 1)
        title = title[1][0:(len(title[1]) - 1)]
        if len(title) > 20:
            title = "In Progress"
        # print(title)

        stat = {}

        def instert(id, value, result, dict):
            if not id in dict:
                dict[id] = [value, result]
            else:
                dict[id].append([value, result])

        for i in range(0, len(list_id)):
            substring = soup.find_all("tr", {"id": list_id[i]})
            # print(list_id[i])
            value = re.findall('value=".*?"', str(substring))
            # print(value)
            value = value[2].split(" ", 1)
            value = value[0].split('value="', 1)[1]

            if value is '"':
                value = re.findall('value=".*?"', str(substring))
                value = value[1].split(" ", 1)
                value = value[0].split('value="', 1)[1]

            # print(value)
            title = re.findall('title=".*?"', str(substring))
            title = title[0].split('"', 1)
            title = title[1][0:(len(title[1]) - 1)]
            if len(title) > 20:
                # print("I am here")
                if " of " in title:
                    # print("Gottcha")
                    title = "In Progress"
            # print(title)
            instert(id=list_id[i], value=value, result=title, dict=stat)

        # print(stat)
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(stat)

        return stat


    def status(self, ip_machine):

        self.ip = ip_machine
        agent_link = None
        self.status_of_the_job = None
        job_status = None
        job_name = None
        event_status = ''
        event_name = None
        active_event = None

        a = self.list_events(ip_machine)
        # print(a)
        b = "661ee30c-72c5-402e-8472-5589a6e66943"
        # print(a.get(b)[0])
        try:
            while self.last_job_attr == self.list_events(ip_machine):
                #print("Equal")
                time.sleep(10)
            # print("New event received")
            test = self.list_events(ip_machine)
            for item in test:
                if item not in self.last_job_attr:
                    while event_status not in ("Succeeded", "Error"):
                        active_event = item
                        # print test.get(item)
                        event_status = test.get(item)[1] # return status of the event
                        event_name = test.get(item)[0] # return name of the event
                        # print(event_status)
                        time.sleep(0.1)
                        test = self.list_events(ip_machine)
        except:
            raise Exception
        # print("Completed")
        #print(active_event)
        #print(event_status)
        #print(event_name)





        # WebDriverWait(self.driver, self.short_timeout).until(
        #     EC.presence_of_element_located((By.ID, "taskGrid")))
        #
        # time.sleep(0.5)
        #
        # while job_status not in ("Succeeded", "Error"):
        #     time.sleep(10)
        #     html = self.driver.page_source
        #     soup = BeautifulSoup(html, "html.parser")
        #     substring = soup.find_all('tr', attrs={'id': re.compile(self.job_id + '-')})
        #     status = re.split('title="\/*', str(substring))
        #     print(status)
        #     exit(1)
        #     while status[1] is None:
        #         print("status[1] is None")
        #         html = self.driver.page_source
        #         soup = BeautifulSoup(html, "html.parser")
        #         substring = soup.find_all('tr', attrs={
        #             'id': re.compile(self.job_id + '-')})
        #         status = re.split('title="\/*', str(substring))
        #     status = re.split('" ', str(status[1]))
        #     job_status = status[0]

        if event_status == "Error":
            raise Exception(
                "The %s status has been received for the job: %s." % (event_status, event_name))

        elif event_status == "Succeeded":
            print("The job %s is completed with the %s status" % (event_name, event_status))

        else:
            raise Exception("Unknown status %s for the job %s" % (event_status, event_name))


        #self.job_status = event_status
        #print(self.job_id + " IS JOB ID OF THE LAST RUNNING JOB")



    def core_status(self, ip_machine):

        self.ip = ip_machine
        agent_link = None
        self.status_of_the_job = None
        job_status = None
        job_name = None
        event_status = ''
        event_name = None
        active_event = None

        while self.last_job_attr == self.core_events(ip_machine):
            time.sleep(3)
            print('1')
        test = self.core_events(ip_machine)
        for item in test:
            if item not in self.last_job_attr:
                while event_status not in ("Succeeded", "Error"):
                    active_event = item
                    event_status = test.get(item)[1] # return status of the event
                    event_name = test.get(item)[0] # return name of the event
                    #print(event_status)
                    time.sleep(0.1)
                    print('2')
                    test = self.core_events(ip_machine)

        if event_status == "Error":
            raise Exception(
                "The %s status has been received for the job: %s." % (event_status, event_name))

        elif event_status == "Succeeded":
            print("The job %s is completed with the %s status" % (event_name, event_status))

        else:
            raise Exception("Unknown status %s for the job %s" % (event_status, event_name))






    def rollback(self, ip_machine):
        '''In this function we get id of the job from the events of the 
              dedicated agent and gets the original job id we can use in future.
              Without this function we cannot proceed in the get resolution
              status of the job.'''
        self.ip = ip_machine

        self.ip_cd = ip_livecd
        self.pass_cd = pass_livecd

        agent_link = None

        self.find_machine_link(self.ip)

        self.find_last_job_id()

        self.driver.get(str(self.agent_link + "/RecoveryPoints"))
        time.sleep(7)

        WebDriverWait(self.driver, self.short_timeout).until(EC.text_to_be_present_in_element((By.XPATH, ".//*[@id='content']/div[2]/div[2]/div[1]/span"), "Recovery Points"))
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        substring = soup.find_all('button', {"class": "btn dropdown-toggle"})
        status = re.split('type=*', str(substring))
        status = re.split('"', str(status[0]))
        # print(status)
        select = self.driver.find_element_by_xpath(".//*[@id='" + status[5] + "']")
        select.click()

        time.sleep(1)

        # dm = self.driver.find_elements_by_class_name("dropdown-menu")
        # for elem in dm:
        #     if elem.text is not u'':
        #         elem.find_element_by_link_text("Restore").click()
        # time.sleep(7)

        restore_button = None
        dm = self.driver.find_elements_by_class_name("dropdown-menu")
        for elem in dm:
            if elem.text is not u'':
                restore_button = elem.find_element_by_link_text("Restore")
                while restore_button == None:
                    dm = self.driver.find_elements_by_class_name(
                        "dropdown-menu")
                    for elem in dm:
                        if elem.text is not u'':
                            restore_button = elem.find_element_by_link_text(
                                "Restore")

        restore_button.click()

        time.sleep(7)

        self.wait_for_element_invisible("lpLoadingContent")
        WebDriverWait(self.driver, self.long_timeout).until(EC.element_to_be_clickable((By.ID, "btnWizardDefault")))
        WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.ID, "btnWizardDefault")))
        next_rollback = self.driver.find_element_by_id("btnWizardDefault")
        next_rollback.click()

        self.wait_for_element_invisible(element_id="lpLoadingContent")
        time.sleep(2)

        # WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.XPATH, ".//*[@id='advancedVolumeMapping']/a/span")))
        # WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.XPATH, ".//*[@id='btnWizardDefault']/a/span")))
        restore_text_to_check = self.driver.find_element_by_class_name("wizard-header-info")
        while restore_text_to_check.text != "Select the volumes to recover and where to restore them.":
            time.sleep(1)
            restore_text_to_check = self.driver.find_element_by_class_name(
                "wizard-header-info")

        else:
            next_volume_mapping = WebDriverWait(self.driver,
                                                self.short_timeout).until(
                EC.presence_of_element_located(
                    (By.XPATH, ".//*[@id='btnWizardDefault']")))
            next_volume_mapping.click()
            time.sleep(1)


        WebDriverWait(self.driver, self.long_timeout).until(EC.element_to_be_clickable((By.ID, "btnWizardDefault")))
        next_volume_mapping = self.driver.find_element_by_id("btnWizardDefault")
        next_volume_mapping.click()
        time.sleep(1)
        try:
            popup_header = self.driver.find_element_by_id("msgbox-message-header")

            if "Error" in popup_header.text:
                raise Exception("I have received Error for the rollback job")
        except NoSuchElementException:
            pass

        WebDriverWait(self.driver, self.long_timeout).until(EC.element_to_be_clickable((By.ID, "isIUnderstand")))
        # WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.ID, "isIUnderstand")))
        accept_warning = self.driver.find_element_by_id("isIUnderstand")
        accept_warning.click()
        time.sleep(1)

        WebDriverWait(self.driver, self.long_timeout).until(EC.element_to_be_clickable((By.ID, "btnWizardDefault")))
        finish_rollback = self.driver.find_element_by_id("btnWizardDefault")
        finish_rollback.click()

        self.wait_for_element_invisible("lpLoadingContent")

        popup_header = self.driver.find_element_by_id("msgbox-message-header")

        if "Error" in popup_header.text:
            raise Exception("I have received Error for the rollback job")

        time.sleep(5)
        print("COMPLETED ROLLBACK")

    def auto_bmr(self, ip_machine, vbox_vmname, ip_livecd, pass_livecd):
        '''In this function we get id of the job from the events of the 
                    dedicated agent and gets the original job id we can use in future.
                    Without this function we cannot proceed in the get resolution
                    status of the job.'''
        self.ip = ip_machine
        self.vmname = vbox_vmname
        self.ip_cd = ip_livecd
        self.pass_cd = pass_livecd
        agent_link = None
        self.find_machine_link(self.ip)
        self.find_last_job_id()
        status_vm = "vboxmanage showvminfo " + self.vmname + " | grep State: | awk '{print $2}'"
        start_vm = "vboxmanage startvm " + self.vmname + " --type gui"
        boot_vm_dvd = "vboxmanage modifyvm " + self.vmname + " --boot1 dvd"
        restore_snap = "vboxmanage snapshot " + self.vmname + " restore clear"
        poweroff_vm = "vboxmanage controlvm " + self.vmname + " poweroff"


        print("Working here")

        status = self.execute.execute(cmd=status_vm)[0][0]

        status = status.split()[0]

        print status

        if status in ['powered', 'saved', 'aborted']:
            # Sometimes machine appears to be aborted. To avoid this,
            # we use restore to the snapshot.
            if "aborted" in status:
                self.execute.execute(cmd=restore_snap)
                print("Snapshot restored")
                time.sleep(5)
            if "powered" in status:
                self.execute.execute(cmd=boot_vm_dvd)
                time.sleep(10)
                print("LiveDVD machine is configured to boot from LiveDVD")

                self.execute.execute(cmd=restore_snap)
                print("Snapshot restored")
                time.sleep(5)

            self.execute.execute(cmd=start_vm)
            time.sleep(5)
            print("LiveDVD machine booting from the dvd")

        self.find_last_job_id()
        self.driver.get(str(self.agent_link + "/RecoveryPoints"))
        time.sleep(7)

        WebDriverWait(self.driver, self.short_timeout).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, ".//*[@id='content']/div[2]/div[2]/div[1]/span"),
                "Recovery Points"))
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        #substring = soup.find_all('button', {"class": "btn dropdown-toggle"}) '''worked in 7.0.0 and not working in 6.1.3'''
        substring = soup.find_all('button', {"type": "button"})
        # print substring
        status = re.split('type=*', str(substring))
        status = re.split('"', str(status[0]))
        # print(status)
        select = self.driver.find_element_by_xpath(
            ".//*[@id='" + status[5] + "']")
        select.click()

        time.sleep(1)

        # dm = self.driver.find_elements_by_class_name("dropdown-menu")
        # for elem in dm:
        #     if elem.text is not u'':
        #         elem.find_element_by_link_text("Restore").click()
        # time.sleep(7)

        restore_button = None
        dm = self.driver.find_elements_by_class_name("dropdown-menu")
        for elem in dm:
            if elem.text is not u'':
                restore_button = elem.find_element_by_link_text("Restore")
                while restore_button == None:
                    dm = self.driver.find_elements_by_class_name(
                        "dropdown-menu")
                    for elem in dm:
                        if elem.text is not u'':
                            restore_button = elem.find_element_by_link_text(
                                "Restore")

        restore_button.click()

        #print("Restore button has been clicked.")

        self.wait_for_element_invisible("lpLoadingContent")
        WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.ID, "recoverUsingBootCD")))
        bootcd = self.driver.find_element_by_id("recoverUsingBootCD")
        bootcd.click()

        WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.ID, "alredyHaveBootCD")))
        comfirm = self.driver.find_element_by_id("alredyHaveBootCD")
        comfirm.click()

        ip_addr = self.driver.find_element_by_id("ipAddress")
        ip_addr.send_keys(self.ip_cd)

        ip_addr = self.driver.find_element_by_id("authenticationKey")
        ip_addr.send_keys(self.pass_cd)

        WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.ID, "btnWizardDefault")))
        next = self.driver.find_element_by_id("btnWizardDefault")
        next.click()

        self.wait_for_element_invisible("lpLoadingContent")

        popup_header = self.driver.find_element_by_id("msgbox-message-header")
        popup = self.driver.find_element_by_id("msgbox-message")

        #print(popup.is_enabled())
        # print(popup)
        #print(popup.text)

        '''Popup.text may have empty string.'''
        if "Dynamic disks will be converted into basic during restoration" in popup.text:

            self.driver.find_element_by_class_name("default").click()
            self.driver.find_element_by_id("restoretionDisksMappingGrid_selectAll_triSpan").click()
            self.driver.find_element_by_id("targetDisksGrid_selectAll_triSpan").click()

        elif "Error" in popup_header.text:
            print("Error for connection to the LiveDVD is received: %s\n" % popup.text)
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            error_message = soup.find_all('p', {"id": "msgbox-stacktrace"})
            print error_message
            exit(1)

        WebDriverWait(self.driver, self.short_timeout).until(
            EC.element_to_be_clickable((By.ID, "btnWizardDefault")))
        next = self.driver.find_element_by_id("btnWizardDefault")
        next.click()

        WebDriverWait(self.driver, self.short_timeout).until(
            EC.element_to_be_clickable((By.ID, "btnWizardDefault")))
        next = self.driver.find_element_by_id("btnWizardDefault")
        next.click()

        WebDriverWait(self.driver, self.short_timeout).until(
            EC.element_to_be_clickable((By.ID, "btnWizardDefault")))
        next = self.driver.find_element_by_id("btnWizardDefault")
        next.click()

        WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.ID, "isIUnderstand")))
        self.driver.find_element_by_id("isIUnderstand").click()
        time.sleep(2)

        WebDriverWait(self.driver, self.short_timeout).until(
            EC.element_to_be_clickable((By.ID, "btnWizardDefault")))
        finish = self.driver.find_element_by_id("btnWizardDefault")
        finish.click()

        self.wait_for_element_invisible(element_id="lpLoadingContent")
        popup = self.driver.find_element_by_id("msgbox-message")
        # print(popup)
        #print(popup.text)
        if "The type of source BIOS" in popup.text:
            print("I am in popup.text")
            self.firmware = "EFI"
            self.driver.find_element_by_id("1").click()
        else:
            self.firmware = "BIOS"
        time.sleep(5)
        print('BMR is started.......')


    def export_vbox(self, ip_machine, vbox_export_vmname, ip_livecd, pass_livecd):
        '''In this function we get id of the job from the events of the 
                    dedicated agent and gets the original job id we can use in future.
                    Without this function we cannot proceed in the get resolution
                    status of the job.'''
        self.ip = ip_machine
        self.vmname = vbox_export_vmname
        self.ip_cd = ip_livecd
        self.pass_cd = pass_livecd
        agent_link = "https://10.10.61.30:8006/apprecovery/admin/ProtectedMachines/482a0a91-b82d-494f-ac6a-ebc542435cdc"
        self.find_machine_link(self.ip)
        self.find_last_job_id()

        status_vm = "vboxmanage showvminfo " + self.vmname + " | grep State: | awk '{print $2}'"
        start_vm = "vboxmanage startvm " + self.vmname + " --type gui"
        boot_vm_dvd = "vboxmanage modifyvm " + self.vmname + " --boot1 dvd"
        restore_snap = "vboxmanage snapshot " + self.vmname + " restore clear"
        poweroff_vm = "vboxmanage controlvm " + self.vmname + " poweroff"


        # print("Working here")
        #
        # status = self.execute(cmd=status_vm)[0][0]
        #
        # status = status.split()[0]
        #
        # print status
        #
        # if status in ['powered', 'saved']:
        #     print "Truesss"
        #     if "powered" in status:
        #         self.execute(cmd=boot_vm_dvd)
        #         time.sleep(10)
        #         print("LiveDVD machine is configured to boot from LiveDVD")
        #
        #         self.execute(cmd=restore_snap)
        #         print("Snapshot restored")
        #         time.sleep(5)
        #
        #     self.execute(cmd=start_vm)
        #     print("LiveDVD machine booting from the dvd")

        self.find_last_job_id()
        self.driver.get(str(self.agent_link + "/RecoveryPoints"))
        time.sleep(7)

        WebDriverWait(self.driver, self.short_timeout).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, ".//*[@id='content']/div[2]/div[2]/div[1]/span"),
                "Recovery Points"))
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        #substring = soup.find_all('button', {"class": "btn dropdown-toggle"}) '''worked in 7.0.0 and not working in 6.1.3'''
        substring = soup.find_all('button', {"type": "button"})
        # print substring
        status = re.split('type=*', str(substring))
        status = re.split('"', str(status[0]))
        # print(status)
        select = self.driver.find_element_by_xpath(
            ".//*[@id='" + status[5] + "']")
        select.click()

        time.sleep(1)

        # dm = self.driver.find_elements_by_class_name("dropdown-menu")
        # for elem in dm:
        #     if elem.text is not u'':
        #         elem.find_element_by_link_text("Restore").click()
        # time.sleep(7)

        export_button = None
        dm = self.driver.find_elements_by_class_name("dropdown-menu")
        for elem in dm:
            if elem.text is not u'':
                export_button = elem.find_element_by_link_text("Export")
                while export_button == None:
                    dm = self.driver.find_elements_by_class_name(
                        "dropdown-menu")
                    for elem in dm:
                        if elem.text is not u'':
                            export_button = elem.find_element_by_link_text(
                                "Export")

        export_button.click()

        print("Export button has been clicked.")

        self.wait_for_element_invisible("lpLoadingContent")
        WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.ID, "wizardContentContainer")))

        vbox_button = None
        WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.CLASS_NAME, "controls")))

        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        # substring = soup.find_all('button', {"class": "btn dropdown-toggle"}) '''worked in 7.0.0 and not working in 6.1.3'''
        substring = soup.find_all('select', {"class": "form-control ui-widget ui-adropdown"})
        # print substring

        # click = self.driver.find_element_by_id('recoverToVirtualMachine')
        # click.click()

        select = Select(self.driver.find_element_by_id('recoverToVirtualMachine'))
        # print select.options
        for o in select.options:
            # print o.text
            if 'VirtualBox' in o.text:
                # print "Yes"
                # print o
                o.click()
                self.driver.find_element_by_id("btnWizardDefault").click()
                WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.ID, "useRemoteLinuxMachine")))
                self.driver.find_element_by_id('useRemoteLinuxMachine').click()
                self.driver.find_element_by_id('vBoxHostName').send_keys('10.10.60.193')
                self.driver.find_element_by_id('virtualMachineName').send_keys(Keys.LEFT_CONTROL, 'a')
                self.driver.find_element_by_id('virtualMachineName').send_keys(self.vmname)
                self.driver.find_element_by_id('vBoxTargetPath').send_keys('/home/mbugaiov/Music')
                self.driver.find_element_by_id('vBoxUsername').send_keys('root')
                self.driver.find_element_by_id('vBoxPassword').send_keys('111111')
                self.driver.find_element_by_id("btnWizardDefault").click()
                #new page Volumes
                WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.ID, "exportVolumeMappingGrid_selectAll_triSpan")))
                self.driver.find_element_by_id('exportVolumeMappingGrid_selectAll_triSpan').click()
                self.driver.find_element_by_id("btnWizardDefault").click()
                #new_page Warnings

                self.wait_for_element_invisible("lpLoadingContent")
                WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.ID, "btnWizardDefault")))
                self.driver.find_element_by_id("btnWizardDefault").click()
                print("I have adjusted all export tasks")
                break



        print('VBOX export is started.......')

    # def export_vbox_bootable2(self, ip_machine, vbox_export_vmname):
    #
    #     self.vmname = vbox_export_vmname
    #     self.ip = ip_machine
    #     self.ip_cd = ip_livecd
    #     self.pass_cd = pass_livecd
    #     self.bootability = None
    #
    #
    #     # poweroff_vm = "vboxmanage controlvm " + self.vmname + " poweroff"
    #     # start_vm = "vboxmanage startvm " + self.vmname + " --type gui"
    #     # boot_vm_dvd = "vboxmanage modifyvm " + self.vmname + " --boot1 dvd"
    #     # boot_vm_disk = "vboxmanage modifyvm " + self.vmname + " --boot1 disk"
    #     # restore_snap = "vboxmanage snapshot " + self.vmname + " restore clear"
    #     # status_vm = "vboxmanage showvminfo " + self.vmname + " | grep State: | awk '{print $2}'"
    #     # clean_dvd = "sudo vboxmanage storageattach livedvd --storagectl " + "IDE " + "--port 1 --device 0 --type dvddrive --medium " + "emptydrive"
    #     # check_dvd_port = "sudo vboxmanage showvminfo livedvd | grep .iso"
    #     try:
    #
    #         find_ip_exported_vm = "vboxmanage guestproperty enumerate " + self.vmname + " | grep 'IP' | awk '{print $4}' | cut -f1 -d ','"
    #
    #         start_exported_vm = "vboxmanage startvm " + self.vmname
    #
    #         modify_exported_vm = "vboxmanage modifyvm " + self.vmname + " --nic2 bridged --bridgeadapter2 enp3s0 --nictype2 82540EM --macaddress2 080027C4C399 --cableconnected2 on"
    #
    #         self.execute(cmd=modify_exported_vm)
    #         self.execute(cmd=start_exported_vm)
    #         ip = self.execute(cmd=find_ip_exported_vm)[0][0]
    #         counter = 0
    #         while not ip and counter < 20:
    #             time.sleep(5)
    #             counter = counter + 1
    #             ip = self.execute(cmd=find_ip_exported_vm)[0][0]
    #
    #         test_connection = "ping -c 1 " + ip
    #
    #         if ip:
    #             # print self.error_code_unix_command(cmd=test_connection)
    #             # print "=============="
    #             if self.execute.error_code_unix_command(cmd=test_connection) is not 0:
    #                 print "The IP is: %s" % ip
    #                 print "The error code is: %s" % self.error_code_unix_command(cmd=test_connection)
    #                 raise Exception("The ping to the exported machine is not etablished, assume something is wrong with the export")
    #         else:
    #             print "The IP is: %s" % ip
    #             print "The error code is: %s" % self.error_code_unix_command(
    #                 cmd=test_connection)
    #             raise Exception("The IP for the exported machine is not received yet. Please investigate")
    #         print "COMPLETED EXPORT BOOTABLE"
    #     # except:
    #     #     pass
    #
    #     finally:
    #         poweroff_exported_vm = "vboxmanage controlvm " + self.vmname + " poweroff"
    #         unregister_exported_vm = "vboxmanage unregistervm " + self.vmname + " --delete"
    #         remove_exported_from_disk = "sudo rm -rf /home/mbugaiov/Music/" + self.vmname
    #         self.execute(cmd=poweroff_exported_vm)
    #         time.sleep(10)
    #
    #         self.execute(cmd=unregister_exported_vm)
    #         time.sleep(5)
    #
    #         self.execute(cmd=remove_exported_from_disk)
    #         print("Competed cleanup")

    def export_vbox_bootable(self, ip_machine, vbox_export_vmname):

        self.vm = vbox_export_vmname
        self.ip = ip_machine
        self.ip_cd = ip_livecd
        self.pass_cd = pass_livecd
        self.bootability = None

        # poweroff_vm = "vboxmanage controlvm " + self.vmname + " poweroff"
        # start_vm = "vboxmanage startvm " + self.vmname + " --type gui"
        # boot_vm_dvd = "vboxmanage modifyvm " + self.vmname + " --boot1 dvd"
        # boot_vm_disk = "vboxmanage modifyvm " + self.vmname + " --boot1 disk"
        # restore_snap = "vboxmanage snapshot " + self.vmname + " restore clear"
        # status_vm = "vboxmanage showvminfo " + self.vmname + " | grep State: | awk '{print $2}'"
        # clean_dvd = "sudo vboxmanage storageattach livedvd --storagectl " + "IDE " + "--port 1 --device 0 --type dvddrive --medium " + "emptydrive"
        # check_dvd_port = "sudo vboxmanage showvminfo livedvd | grep .iso"

        try:
            self.virtualbox.modify_vm(vmname=self.vm)
            self.virtualbox.start_vm(vmname=self.vm)
            self.virtualbox.ping_vm(vmame=self.vm)

        except Exception as E:
            print traceback.extract_stack()
            print E
            raise Exception

        finally:
            self.virtualbox.poweroff_vm(vmname=self.vm)
            time.sleep(10)
            self.virtualbox.unregister_vm(vmname=self.vm)
            time.sleep(5)
            self.virtualbox.remove_from_disk_vm(vmname=self.vm)
            print("Competed cleanup")


    # def error_code_unix_command(self, cmd=None):
    #     # type: (object) -> object
    #     if cmd is not None:
    #         self.cmd = cmd
    #     p = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE,
    #                          stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    #     #((output, err), code)
    #     (output, err) = p.communicate(input="{}\n".format("Y")), p.returncode
    #     # print("OUT=", output)
    #     #print(output)
    #     # p.stdin.write("Y\n")
    #     p_status = p.wait()
    #     #error_code = p.communicate()[0]
    #     return (p.poll())
    #
    # def execute(self, cmd=None):
    #     # type: (object) -> object
    #     if cmd is not None:
    #         self.cmd = cmd
    #     p = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE,
    #                          stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    #     #((output, err), code)
    #     (output, err) = p.communicate(input="{}\n".format("Y")), p.returncode
    #     # print("OUT=", output)
    #     # print(output)
    #     # print(err)
    #     # p.stdin.write("Y\n")
    #     p_status = p.wait()
    #     #error_code = p.communicate()[0]
    #     if err not in (0, 100):
    #         raise Exception("Exception: '%s' command finished with error code %d" %(self.cmd, err))
    #     else:
    #         return (output, err)

    def prepare_livedvd(self):
        download_link = "wget https://raw.github.com/mbugaiov/myrepo/master/Livedvd_download.sh"
        chmod_sh = "chmod +x Livedvd.iso"
        folder_custom = "mkdir /tmp/livedvd_custom"
        folder_mount = "mkdir /mnt/livedvd_custom"
        mount_cd = "mount -t iso9660 -o loop Livedvd.iso /mnt/livedvd_custom"
        folder_mount_cd = "cd /mnt/livedvd_custom"
        tar = "sudo tar cf - . | sudo tar xfp - -C /tmp/livedvd/"
        cd_squash = "cd /tmp/livedvd/casper"
        mkdir = "mkdir squashfs-temp"
        cd = "cd squashfs-temp"
        unsquash = "sudo unsquashfs ../filesystem.squashfs"
        cp_passwd = "sudo cp /home/mbugaiov/Desktop/passwd squashfs-root/etc/passwd"
        cp_shadow = "sudo cp /home/mbugaiov/Desktop/shadow squashfs-root/etc/shadow"
        mksquash = "mksquashfs squashfs-root/ filesystem.squashfs -noappend -always-use-fragments"
        move = "mv filesystem.squashfs ../"
        cd_down = "cd .."
        remove = "rm -rf squashfs-temp/"


    def bmr_bootable(self, ip_machine, ip_livecd, pass_livecd, vbox_vmname):
        self.vmname = vbox_vmname
        self.ip = ip_machine
        self.ip_cd = ip_livecd
        self.pass_cd = pass_livecd
        self.bootability = None
        counter = 0
        poweroff_vm = "vboxmanage controlvm " + self.vmname + " poweroff"
        start_vm = "vboxmanage startvm " + self.vmname + " --type gui"
        boot_vm_dvd = "vboxmanage modifyvm " + self.vmname + " --boot1 dvd"
        boot_vm_disk = "vboxmanage modifyvm " + self.vmname + " --boot1 disk"
        restore_snap = "vboxmanage snapshot " + self.vmname + " restore clear"
        status_vm = "vboxmanage showvminfo " + self.vmname + " | grep State: | awk '{print $2}'"
        clean_dvd = "sudo vboxmanage storageattach livedvd --storagectl " + "IDE " + "--port 1 --device 0 --type dvddrive --medium " + "emptydrive"
        check_dvd_port = "sudo vboxmanage showvminfo livedvd | grep .iso"

        try:
            status = self.execute.execute(cmd=status_vm)[0][0]
            if "running" in status:
                self.virtualbox.poweroff_vm(vmname=self.vmname)
                time.sleep(10)
            self.virtualbox.boot_disk_vm(vmname=self.vmname)
            print("Machine settings: Boot from disk")
            time.sleep(10)
            self.virtualbox.clean_dvd_vm(vmname=self.vmname)
            time.sleep(5)
            print('The firmware of the machine is: %s' % self.firmware)

            '''Configuring EFI firmware in case if source machine is EFI'''
            if self.firmware is "EFI":
                self.virtualbox.set_firmware_vm(vmname=self.vmname, firmware="efi")

            self.virtualbox.start_vm(vmname=self.vmname)
            print("Machine started")

            '''Check the IP adress of the machine. Needs to ping it after boot
            to make sure that machine is reachable.'''

            self.virtualbox.ping_vm(vmame=self.vmname)

        except Exception as E:
            print traceback.extract_stack()
            print E
            raise Exception

        finally:

            #TODO Investigate is it possible to remove poweroff_vm and boot_vm_dvd and start only from the restore_snap.

            self.virtualbox.poweroff_vm(vmname=self.vmname)
            print("Machine poweroff")
            time.sleep(10)
            self.virtualbox.boot_dvd_vm(vmname=self.vmname)
            print("Machine settings: Boot from dvd")
            time.sleep(10)
            self.virtualbox.restore_snap_vm(vmname=self.vmname)
            print("Snapshot restored")
            time.sleep(5)
            self.virtualbox.start_vm(vmname=self.vmname)
            print("Completed")
            self.virtualbox.poweroff_vm(vmname=self.vmname)
            print("Machine poweroff")



