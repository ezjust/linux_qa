# -- FILE: features/steps/example_steps.py
# -*- coding: utf-8 -*-
from selenium import webdriver
import os, time
import string
from behave import given, when, then, step
import system
import localmount

unix = system.Execute()
lmount = localmount.Lmount()

@when('visit url "{url}"')
def step(context, url):
    context.browser = webdriver.Firefox()
    context.browser.get(url)

@when('field with name "{selector}" is given "{value}"')
def step(context, selector, value):
    elem = context.browser.find_element_by_name(selector)
    elem.send_keys(value)
    elem.submit()
    time.sleep(2)

@then('title becomes "{title}"')
def step(context, title):
    assert context.browser.title == title

@then('close')
def close(context):
    context.browser.quit()

@given('download "{script}"')
def step(context, script):
    unix.execute('wget https://raw.github.com/mbugaiov/linux-qa-scripts/master/' + script)
    #os.system('wget https://raw.github.com/mbugaiov/linux-qa-scripts/master/' + script)

@given('run "{script}" option "{option}" branch "{branch}"')
def step(context, script, option, branch):
    unix.execute('chmod +x ./' + script)
    unix.execute('sudo ./' + script + " --" + option + " --branch=" + branch)

@when('installed package "{package}"')
def step(context, package):
    try:
        assert unix.package_installed(package_name=package)
    except AssertionError:
        raise Exception("The package %s is not installed" % package)

@then('remove "{script}"')
def step(context, script):
    unix.execute('rm -rf ' + script)

@then('list machines on the "{ip}", user "{user}", password "{password}"')
def step(context, ip, user, password):
    assert "Host/Adress" in unix.execute('sudo local_mount ' + user + ':' + password + '@' + ip + ' lm')

@then('list recovery points on the "{ip}", user "{user}", password "{password}", machine number "{mnumber}"')
def step(context, ip, user, password, mnumber):
    '''Date and Status rows will be in case, if machine has at least 1 recovery point'''
    assert "Status" in unix.execute('sudo local_mount ' + user + ':' + password + '@' + ip + ' lr ' + mnumber)

@then('list recovery points on the "{ip}", user "{user}", password "{password}", machine name "{mname}"')
def step(context, ip, user, password, mname):
    '''Date and Status rows will be in case, if machine has at least 1 recovery point'''
    mnumber = None
    output = unix.execute('sudo local_mount ' + user + ':' + password + '@' + ip + ' lm')
    for line in output.splitlines():
        if mname in line:
            mnumber = (" ".join(line.split())).split(" ")[0]
            print mnumber
    if mnumber:
        assert "Status" in unix.execute('sudo local_mount ' + user + ':' + password + '@' + ip + ' lr ' + mnumber)

@then('mount recovery points of the "{ip}", user "{user}", password "{password}", machine number "{mnumber}"')
def step(context, ip, user, password, mnumber):
    '''Date and Status rows will be in case, if machine has at least 1 recovery point'''
    lmount.mount_by_mnumber(ip, user, password, mnumber)

@then('mount recovery points of the "{ip}", user "{user}", password "{password}", machine name "{mname}"')
def step(context, ip, user, password, mname):
    '''Date and Status rows will be in case, if machine has at least 1 recovery point'''
    mnumber = None
    output = unix.execute('sudo local_mount ' + user + ':' + password + '@' + ip + ' lm')
    for line in output.splitlines():
        if mname in line:
            mnumber = (" ".join(line.split())).split(" ")[0]
            print mnumber
    if mnumber:
        lmount.mount_by_mnumber(ip, user, password, mnumber)
    else:
        raise Exception('The machine %s was not found' % mname)
