import splinter
import selenium
import subprocess
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains


from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import re
import urllib


link = 'https://10.10.61.20:8006/apprecovery/admin'
# driver.implicitly_wait(10) # seconds


class WebAgent(object):
    short_timeout = 60
    long_timeout = 200
    agent_link = None
    id_agent = None




    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.driver.get(link)

    def open_core_ui(self):
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            asd = self.driver.switch_to_alert()
            asd.send_keys("Administrator")
            asd.send_keys(Keys.TAB + '123asdQ')
            asd.accept()
            print("Core UI is open")

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

    def find_machine_link(self):
        print("I am in find machine link")
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
                if elem.text in [self.ip]:
                    self.agent_link = test
                    self.id_agent = re.split(r'Machines/*', self.agent_link)[1]
                    # print "AGENT LINK", self.agent_link
                    return self.agent_link
            except Exception:
                continue
            # print("self.ip  is up")

    def find_machine_link2(self):
        print("I am in find machine link")
        WebDriverWait(self.driver, self.long_timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'a')))
        try:
            set_of_machine = self.driver.find_element(By.ID,
                                                      "apgProtected").find_elements_by_tag_name(
                'a')
            # print set_of_machine
            for elem in set_of_machine:

                test = elem.get_attribute('href')
                # print test
                # print elem.text
                # print(self.ip)
                # print("self.ip  is up")
                if elem.text in self.ip:
                    self.agent_link = test
                    self.id_agent = re.split('Machines/*', self.agent_link)[1]
                    # print(self.agent_link)
                    return (self.agent_link)
        except selenium.common.exceptions.StaleElementReferenceException:
            pass

    def find_last_job_id(self):

        """We are looking in events the last one job_id. This job_id we can use is compare with the current one job id, to make sure, that we parse the status of the appropriate job.
        Here is output of the this job id : 405bf1d0-e552-4b3f-8dc6-f8a4f2310d8f
        """
        current_page = self.driver.current_url
        if self.agent_link is not None:
            self.driver.get(str(self.agent_link + "/Events"))
        if self.driver.current_url is not str(self.agent_link + "/Events"):

            time.sleep(10)

        time.sleep(2)

        WebDriverWait(self.driver, self.short_timeout).until(
            EC.presence_of_element_located((By.ID, "taskGrid")))
        try:
            event_grid = self.driver.find_element_by_id(
                'taskGrid').find_elements_by_tag_name('tr')
            for elem in event_grid:
                test = elem.get_attribute('td')
                # print(elem.text)

            last_job = self.driver.find_element_by_id(
                'taskGrid').find_elements_by_tag_name('tr')
            while last_job is None:
                last_job = self.driver.find_element_by_id(
                    'taskGrid').find_elements_by_tag_name('tr')
            # last_job_attr = last_job[0].get_attribute('td')
            # for n in last_job:
            # print(n.get_attribute('id'))
            try:
                check = last_job[1]
                check = last_job[1]
                last_job_attr = check.get_attribute('id')
                last_job_open = self.driver.find_element_by_xpath(
                    ".//*[@id='" + last_job_attr + "']/td[7]/div")
                print(
                    last_job_attr + " This is job ID of the last event is the events before active call of the new")
                self.last_job_attr = last_job_attr

            except IndexError:
                self.last_job_attr = 'null'

            return self.last_job_attr


        except selenium.common.exceptions.StaleElementReferenceException:
            pass
        finally:
            self.driver.get(current_page)
            time.sleep(2)








    def protect_new_agent(self, ip, username, password):

        self.ip = ip
        self.username = username
        self.password = password
        agent_link = None
        id = None


        try:
            print("I am starting to protect agent %s, %s, %s" % (self.ip, self.username, self.password))
            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='protectMachine']/div[1]/span")))
            new = self.driver.find_element_by_xpath(".//*[@id='protectMachine']/div[1]/span")
            new.click()

            WebDriverWait(self.driver, self.long_timeout).until(EC.text_to_be_present_in_element((By.CLASS_NAME, "wizard-header-info"), "The Protect Machine wizard helps you to quickly and easily protect a machine."))
            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='btnWizardDefault']")))
            next = self.driver.find_element_by_xpath(".//*[@id='btnWizardDefault']")
            next.click()


            WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.XPATH, ".//*[@id='hostName']")))

            hostname = self.driver.find_element_by_xpath(".//*[@id='hostName']")
            hostname.send_keys(self.ip)

            usernm = self.driver.find_element_by_xpath(".//*[@id='userName']")
            usernm.send_keys(self.username)

            passwd = self.driver.find_element_by_xpath(".//*[@id='password']")
            passwd.send_keys(self.password)

            next = self.driver.find_element_by_xpath(".//*[@id='btnWizardDefault']")
            next.click()

            self.wait_for_element_invisible(element_id="lpLoadingContent")

            # WebDriverWait(self.driver, self.short_timeout).until(EC.visibility_of_element_located((By.XPATH, ".//*[@id='btnWizardDefault']"))) # this part should be rechecked. Since, there is bug.

            # WebDriverWait(self.driver, self.short_timeout).until(
            #     EC.presence_of_element_located((By.XPATH, ".//*[@id='wizardContentContainer']/div[2]/div[2]/div/div[1]/div/label/span/text()")))
            upgrade = self.driver.find_element_by_id("wizardContentContainer")
            if upgrade is not None:
                if "The target machine is running an older version of the Quest Rapid Recovery Agent software" in upgrade.text:
                    click_upgrade = self.driver.find_element_by_id("upgradeAgent")
                    click_upgrade.click()

                    print("I was in upgrade section and considered that machine is suitable for upgrade")
                    print(upgrade.text)
                    next_button = self.driver.find_element_by_id("btnWizardDefault")
                    next_button.click()

            time.sleep(2)
            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.ID, "btnWizardBack")))
            back = self.driver.find_element_by_xpath(".//*[@id='btnWizardBack']")
            back.click()

            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='btnWizardDefault']")))
            next = self.driver.find_element_by_xpath(".//*[@id='btnWizardDefault']")
            next.click()

            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='btnWizardDefault']")))
            finish = self.driver.find_element_by_xpath(".//*[@id='btnWizardDefault']")
            finish.click()
            print("The agent %s with the credentials: %s and %s is protected" % (self.ip, self.username, self.password))


            while self.find_machine_link() is None:
                print(self.find_machine_link())
                print("waiting protected machine to appear")
                time.sleep(5)
            print("Machine is protected. New transfer will be started")

            self.driver.get(str(self.agent_link))

            self.find_last_job_id()

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
            every.send_keys("8")

            # WebDriverWait(self.driver, self.short_timeout).until(EC.visibility_of_element_located((By.XPATH, ".//*[@id='content']/div[2]/div[2]/div[1]/span")))
            apply = self.driver.find_element_by_id("protectionScheduleEditOK")
            apply.click()

            print("Schedule is configured")
            # print("HERE1")
            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='machineDetailesToolbar_" + self.id_agent + "']/ul/li[6]/a/span")))
            force_snapshot = self.driver.find_element_by_xpath(".//*[@id='machineDetailesToolbar_" + self.id_agent + "']/ul/li[6]/a/span")
            force_snapshot.click()
            # print("HERE2")
            self.wait_for_element_invisible(element_id="lpLoadingContent")
            # print("HERE3")
            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='machineDetailesToolbar_" + self.id_agent + "']/ul/li[6]/a")))
            first_force = self.driver.find_element_by_xpath(".//*[@id='machineDetailesToolbar_" + self.id_agent + "']/ul/li[6]/a")
            first_force.click()
            # print("HERE4")
            self.wait_for_element_invisible(element_id="lpLoadingContent")
            self.driver.find_element_by_class_name("btn-container").send_keys(Keys.ENTER)
            self.wait_for_element_invisible(element_id="lpLoadingContent")
            # print("HERE5")


        finally:
            pass

    def remove_agent_by_id(self, ip):


        self.ip = ip

        try:

            self.find_machine_link()
            counter = 0
            while self.agent_link == None:
                time.sleep(5)
                self.find_machine_link()
                print("I got 'None' for the agent_link, 'timeout in 60 sec' is applied.")
                counter = counter + 1
                if counter == 12 :
                    self.driver.close()
                    print("There was not found machine for remove.")

            self.driver.get(str(self.agent_link))

            WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.XPATH, ".//*[@id='machineDetailesToolbar_" + self.id_agent + "']/ul/li[10]/a")))
            remove_agent = self.driver.find_element_by_xpath(".//*[@id='machineDetailesToolbar_" + self.id_agent + "']/ul/li[10]/a")
            remove_agent.click()

            time.sleep(2)

            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='popup1']/div/div[6]/form/div[1]/div/div/label/span")))
            click_remove_with_recovery_points = self.driver.find_element_by_xpath(".//*[@id='popup1']/div/div[6]/form/div[1]/div/div/label/span")
            click_remove_with_recovery_points.click()

            WebDriverWait(self.driver, self.short_timeout).until(EC.element_to_be_clickable((By.XPATH, ".//*[@id='btnRemoveProtection']")))
            click_remove_default = self.driver.find_element_by_xpath(".//*[@id='btnRemoveProtection']")
            click_remove_default.click()
            print("The agent removed")
        except OSError as e:
            raise Exception("Something goes wrong with remove of the agent")




    def status(self, ip):
        self.ip = ip
        agent_link = None
        self.status_of_the_job = None
        job_status = None
        job_name = None

        try:
            self.find_machine_link()
            while self.agent_link == None:
                time.sleep(5)
                self.find_machine_link()
                print("I got None for agent_link, while is applied.")
        except OSError as e:
            raise Exception("Here is bug in status with the agent link.")

        self.job_id = self.last_job_attr

        while self.job_id in self.last_job_attr: ##here I try to make check, that new job_id is not the same, as old job in events.

            self.driver.get(str(self.agent_link + "/Events"))
            time.sleep(2)

            WebDriverWait(self.driver, self.long_timeout).until(EC.presence_of_element_located((By.ID, "taskGrid")))
            try:
                last_job = self.driver.find_element_by_id(
                    'taskGrid').find_elements_by_tag_name('tr')

                while len(last_job) <= 1:
                    print(len(last_job))
                    print("last job is None")
                    time.sleep(5)
                    last_job = self.driver.find_element_by_id(
                        'taskGrid').find_elements_by_tag_name('tr')

                check = last_job[1]
                last_job_attr = check.get_attribute('id')
                last_job_open = self.driver.find_element_by_xpath(
                    ".//*[@id='" + last_job_attr + "']/td[7]/div")
                last_job_open.click()
            except selenium.common.exceptions.StaleElementReferenceException:
                pass

            WebDriverWait(self.driver, self.short_timeout).until(
                EC.text_to_be_present_in_element((By.ID, "jqgh_taskGrid_Job"),
                                                 "Name"))
            # WebDriverWait(self.driver, self.short_timeout).until(
            #     EC.presence_of_element_located((By.ID, "taskMonitorContent")))

            time.sleep(5)

            WebDriverWait(self.driver, self.short_timeout).until(
                EC.presence_of_element_located((By.ID, "taskGrid")))
            try:
                event_grid = self.driver.find_element_by_id(
                    'taskGrid').find_elements_by_tag_name('tr')
                # for elem in event_grid:
                # test = elem.get_attribute('td')
                # print(elem.text)
                last_job = self.driver.find_element_by_id(
                    'taskGrid').find_elements_by_tag_name('tr')
                check = last_job[1]
                last_job_attr = check.get_attribute('id')
                last_job_open = self.driver.find_element_by_xpath(
                    ".//*[@id='" + last_job_attr + "']/td[7]/div")
                last_job_open.click()
            except selenium.common.exceptions.StaleElementReferenceException:
                pass

            WebDriverWait(self.driver, self.short_timeout).until(
                EC.text_to_be_present_in_element((By.ID, "jqgh_taskGrid_Job"),
                                                 "Name"))
            WebDriverWait(self.driver, self.short_timeout).until(
                EC.presence_of_element_located((By.ID, "taskMonitorContent")))

            time.sleep(2)

            WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.ID, "taskMonitorContent")))
            try:
                job_name = self.driver.find_element_by_id(
                    'taskMonitorContent').find_elements_by_tag_name('dd')[2].text
                job_status = self.driver.find_element_by_id(
                    'taskMonitorContent').find_elements_by_tag_name('dd')[1].text
            except selenium.common.exceptions.StaleElementReferenceException:
                pass
            # print(job_status)  # here we get job status of the action
            if job_status not in ("Succeeded", "Error"):
                self.job_id = self.driver.find_element_by_id(
                    'taskMonitorContent').find_elements_by_tag_name('dd')[
                    0].text
            else:
                html = self.driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                substring = soup.find_all('a', {"class": "pointer"})
                # print(substring[2])
                substring = str(substring[2]).split('"')[5]
                self.job_id = substring  # returned correct job_id only when job is completed.
            print(
                "This is job id of the task: %s" % self.job_id)


        WebDriverWait(self.driver, self.short_timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'a')))
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

        except selenium.common.exceptions.StaleElementReferenceException:
            pass

        self.driver.get(str(agent_link + "/Events"))
        time.sleep(2)

        WebDriverWait(self.driver, self.short_timeout).until(
            EC.presence_of_element_located((By.ID, "taskGrid")))

        time.sleep(0.5)

        while job_status not in ("Succeeded", "Error"):
            time.sleep(10)
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            substring = soup.find_all('tr', attrs={'id': re.compile(self.job_id + '-')})
            status = re.split('title="\/*', str(substring))
            while status[1] is None:
                print("status[1] is None")
                html = self.driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                substring = soup.find_all('tr', attrs={
                    'id': re.compile(self.job_id + '-')})
                status = re.split('title="\/*', str(substring))
            status = re.split('" ', str(status[1]))
            job_status = status[0]

        if job_status == "Error":
            raise Exception(
                "The %s status has been received for the job: %s." % (job_status, job_name))
        elif job_status == "Succeeded":
            print("The job %s is completed with the %s status" % (job_name, job_status))
        else:
            raise Exception("Unknown status %s for the job %s" % (job_status, job_name))

        self.job_status = job_status
        print(self.job_id + " IS JOB ID OF THE LAST RUNNING JOB")

    def rollback(self, ip):
        '''In this function we get id of the job from the events of the 
              dedicated agent and gets the original job id we can use in future.
              Without this function we cannot proceed in the get resolution
              status of the job.'''
        self.ip = ip

        self.ip_cd = ip_cd
        self.pass_cd = pass_cd

        agent_link = None

        self.find_machine_link()

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

        WebDriverWait(self.driver, self.long_timeout).until(EC.element_to_be_clickable((By.ID, "isIUnderstand")))
        # WebDriverWait(self.driver, self.short_timeout).until(EC.presence_of_element_located((By.ID, "isIUnderstand")))
        accept_warning = self.driver.find_element_by_id("isIUnderstand")
        accept_warning.click()
        time.sleep(1)

        WebDriverWait(self.driver, self.long_timeout).until(EC.element_to_be_clickable((By.ID, "btnWizardDefault")))
        finish_rollback = self.driver.find_element_by_id("btnWizardDefault")
        finish_rollback.click()
        time.sleep(5)
        print("COMPLETED ROLLBACK")

    def auto_bmr(self, ip_cd, pass_cd):
        '''In this function we get id of the job from the events of the 
                    dedicated agent and gets the original job id we can use in future.
                    Without this function we cannot proceed in the get resolution
                    status of the job.'''
        self.ip = ip
        self.vmname = vmname
        self.ip_cd = ip_cd
        self.pass_cd = pass_cd
        agent_link = None
        self.find_machine_link()
        self.find_last_job_id()
        status_vm = "vboxmanage showvminfo " + self.vmname + " | grep State: | awk '{print $2}'"
        start_vm = "vboxmanage startvm " + self.vmname + " --type gui"
        boot_vm_dvd = "vboxmanage modifyvm " + self.vmname + " --boot1 dvd"
        restore_snap = "vboxmanage snapshot " + self.vmname + " restore clear"
        poweroff_vm = "vboxmanage controlvm " + self.vmname + " poweroff"


        print("Working here")

        status = self.execute(cmd=status_vm)[0][0]
        print(status)
        if status in ["powered", "saved"]:
            print "True"
            if "powered" in status:
                self.execute(cmd=boot_vm_dvd)
                time.sleep(10)
                print("LiveDVD machine is configured to boot from LiveDVD")

                self.execute(cmd=restore_snap)
                print("Snapshot restored")
                time.sleep(5)

            self.execute(cmd=start_vm)
            print("LiveDVD machine booting from the dvd")


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
        print substring
        status = re.split('type=*', str(substring))
        status = re.split('"', str(status[0]))
        print(status)
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

        print("Restore button has been clicked.")

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

        print(popup.is_enabled())
        # print(popup)
        print(popup.text)

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
        print(popup.text)
        if "The type of source BIOS" in popup.text:
            print("I am in popup.text")
            self.driver.find_element_by_id("1").click()
        time.sleep(5)

    def error_code_unix_command(self, cmd=None):
        # type: (object) -> object
        if cmd is not None:
            self.cmd = cmd
        p = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        #((output, err), code)
        (output, err) = p.communicate(input="{}\n".format("Y")), p.returncode
        # print("OUT=", output)
        #print(output)
        # p.stdin.write("Y\n")
        p_status = p.wait()
        #error_code = p.communicate()[0]
        return (p.poll())

    def execute(self, cmd=None):
        # type: (object) -> object
        if cmd is not None:
            self.cmd = cmd
        p = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        #((output, err), code)
        (output, err) = p.communicate(input="{}\n".format("Y")), p.returncode
        # print("OUT=", output)
        # print(output)
        # print(err)
        # p.stdin.write("Y\n")
        p_status = p.wait()
        #error_code = p.communicate()[0]
        if err not in (0, 100):
            raise Exception("Exception: '%s' command finished with error code %d" %(self.cmd, err))
        else:
            return (output, err)

    def bmr_bootable(self, ip_cd, pass_cd, vmname):
        self.vmname = vmname
        self.ip = ip
        self.ip_cd = ip_cd
        self.pass_cd = pass_cd
        self.bootability = None
        counter = 0
        poweroff_vm = "vboxmanage controlvm " + self.vmname + " poweroff"
        start_vm = "vboxmanage startvm " + self.vmname + " --type gui"
        boot_vm_dvd = "vboxmanage modifyvm " + self.vmname + " --boot1 dvd"
        boot_vm_disk = "vboxmanage modifyvm " + self.vmname + " --boot1 disk"
        restore_snap = "vboxmanage snapshot " + self.vmname + " restore clear"
        status_vm = "vboxmanage showvminfo " + self.vmname + " | grep State: | awk '{print $2}'"
        try:
            # print(self.error_code_unix_command(cmd=poweroff_vm))
            status = self.execute(cmd=status_vm)[0][0]
            if "running" in status:
                print("I am here")
                self.execute(cmd=poweroff_vm)
                print("Machine poweroff")
                time.sleep(10)
            self.execute(cmd=boot_vm_disk)
            print("Machine settings: Boot from disk")
            time.sleep(10)
            self.execute(cmd=start_vm)
            print("Machine started")


            cmd = "ping -c 1 " + self.ip_cd
            print(cmd)
            # print(self.error_code_unix_command(cmd))
            # print(counter)
            # print("Counter is up")
            while self.error_code_unix_command(cmd) is not 0 and counter <= 60:
                print("Wainting machine to be booted... %i" %counter)
                time.sleep(10)
                counter = counter + 1
                #print(self.error_code_unix_command(cmd))
            else:
                if self.error_code_unix_command(cmd) is 0 and counter <= 60:
                    print("Network connection to the machine is available, assume that BMR is OK")
                    time.sleep(10)
                    self.execute(
                        cmd="vboxmanage controlvm " + self.vmname + " screenshotpng /tmp/bmr.png")
                    self.execute(cmd="display /tmp/bmr.png")
                else:
                    print("Machine was not booted within 10 minutes, assume BMR is FAILED")
                    return 1
            print("Testing of the bootability of the machine is completed.")

        except:
            pass
        finally:
            self.execute(cmd=poweroff_vm)
            print("Machine poweroff")
            time.sleep(10)
            self.execute(cmd=boot_vm_dvd)
            print("Machine settings: Boot from dvd")
            time.sleep(10)
            self.execute(cmd=restore_snap)
            print("Snapshot restored")
            time.sleep(5)
            self.execute(cmd=start_vm)
            print("Completed")





if __name__ == "__main__":
    ip = "10.10.35.168"
    username = "rr"
    password = "123asdQ"
    ip_cd = "10.10.38.10"
    pass_cd = "123asdQQ"
    vmname = "livedvd"

    a = WebAgent()
    try:

        a.open_core_ui()
        # a.protect_new_agent(ip, username, password)
        # a.status(ip)
        for i in range(0,9):
                # a.protect_new_agent(ip, username, password)
                # a.status(ip)
                # a.rollback(ip)
                # a.status(ip)
                a.auto_bmr(ip_cd, pass_cd)
                a.status(ip)
                a.bmr_bootable(ip_cd, pass_cd, vmname)
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


    finally:
        a.driver.get_screenshot_as_file(filename="/tmp/ERROR_image")
        # a.remove_agent_by_id(ip)
        a.driver.close()
        pass

