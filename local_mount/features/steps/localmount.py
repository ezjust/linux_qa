import os, time
import string
import system

unix = system.Execute()

class Lmount(object):

    def __init__(self, cmd=None):
        self.cmd = cmd

    def mount_by_mnumber(self, ip, user, password, mnumber):
        '''Date and Status rows will be in case, if machine has at least 1 recovery point'''
        number = None
        output = unix.execute('sudo local_mount ' + user + ':' + password + '@' + ip + ' lr ' + mnumber)

        def mounter(number):
            unix.execute('sudo mkdir /tmp/first')
            print("===================================================================")
            print(number)
            print("===================================================================")
            for line in output.splitlines():
                ignore_list = ["swap", "Base", "Incremental"]
                if (":" + str(number)) in line and not any(word in line for word in ignore_list):
                    print("-----------")
                    print(line)
                    print("-----------")
                    element = (" ".join(line.split())).split(" ")[
                        5]  # remove muliple spaces and then get the 5 element in string
                    print element
                    unix.execute('sudo local_mount ' + user + ':' + password + '@' + ip + ' m ' + element + ' /tmp/first')
                    list_devices = unix.execute('sudo local_mount ' + user + ':' + password + '@' + ip + ' l')
                    assert '/tmp/first' in list_devices
                    for line in list_devices.splitlines():
                        if '/tmp/first' in line:
                            nbd_device = (" ".join(line.split())).split(" ")[1]
                            print nbd_device
                            unix.execute('sudo local_mount' + ' u ' + nbd_device)
            unix.execute('sudo rm -rf /tmp/first')

        if not "No recovery points were found" in output:
            print output
            for line in output.splitlines():
                if "recovery points" in line:
                    number = line.split(" ")[1]  # the string has next view : Found 2 recovery points:
                    print number

            if number:
                if int(number) == 1:
                    '''Mount only first recovery point'''
                    mounter(number)
                else:
                    '''Mount first and last recovery point'''
                    print "greater"
                    mounter(1)
                    mounter(number)
        else:
            return "No recovery points were found for the specified machine"