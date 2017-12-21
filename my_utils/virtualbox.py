from my_utils.system import *
from my_utils.web import *

class Virtualbox(object):

    execute = Executor()

    def find_ip_vm(self, vmname):
        '''
        :return ip - the IP-adress of the machine. If the IP is not defined, returns None
        '''

        self.vmname = vmname

        try:
            ip = self.execute.execute(
                cmd="vboxmanage guestproperty enumerate " + self.vmname + " | grep 'IP' | awk '{print $4}' | cut -f1 -d ','")[
                0][0]

        except Exception:
            ip = None
            print('None')

        counter = 0
        while not ip and counter < 60:
            time.sleep(5)
            counter += 1
            try:
                ip = self.execute.execute(
                    cmd="vboxmanage guestproperty enumerate " + self.vmname + " | grep 'IP' | awk '{print $4}' | cut -f1 -d ','")[
                    0][0]
                print('None1')
            except IndexError:
                ip = None
                print('None2')
                pass

        if not ip:
            ip = None
            print('IP is NONE')

        return ip

    def ping_vm(self, vmame):

        self.vmname = vmame

        ip = self.find_ip_vm(vmname=self.vmname)

        test_connection = "ping -c 1 " + ip

        if ip:
            if self.execute.error_code(cmd=test_connection) is not 0:
                print "The IP is: %s" % ip
                print "The error code is: %s" % self.execute.error_code(cmd=test_connection)
                raise Exception(
                    "The ping to the machine is not etablished, assume something is wrong with the machine. Seems machine is not reachable by the network")
        else:
            print "The IP is: %s" % ip
            print "The error code is: %s" % self.execute.error_code(cmd=test_connection)
            raise Exception(
                "The IP for the machine is not received yet. Please investigate")
        print "Completed check for the connection to the machine"


    def start_vm(self, vmname):
        self.vmname = vmname
        self.execute.execute(cmd="vboxmanage startvm " + self.vmname)


    def modify_vm(self, vmname):
        self.vmname = vmname
        self.execute.execute(cmd="vboxmanage modifyvm " + self.vmname + " --nic2 bridged --bridgeadapter2 enp3s0 --nictype2 82540EM --macaddress2 080027C4C399 --cableconnected2 on")


    def poweroff_vm(self, vmname):
        self.vmname = vmname
        self.execute.execute(cmd="vboxmanage controlvm " + self.vmname + " poweroff")

    def unregister_vm(self, vmname):
        self.vmname = vmname
        self.execute.execute(cmd="vboxmanage unregistervm " + self.vmname + " --delete")

    def remove_from_disk_vm(self, vmname):
        self.vmname = vmname
        self.execute.execute(cmd="sudo rm -rf /home/mbugaiov/Music/" + self.vmname)

    def boot_dvd_vm(self, vmname):
        self.vmname = vmname
        self.execute.execute(cmd="vboxmanage modifyvm " + self.vmname + " --boot1 dvd")

    def boot_disk_vm(self, vmname):
        self.vmname = vmname
        self.execute.execute(cmd="vboxmanage modifyvm " + self.vmname + " --boot1 disk")

    def restore_snap_vm(self, vmname):
        self.vmname = vmname
        self.execute.execute(cmd="vboxmanage snapshot " + self.vmname + " restore clear")

    def status_vm(self, vmname):
        self.vmname = vmname
        self.execute.execute(cmd="vboxmanage showvminfo " + self.vmname + " | grep State: | awk '{print $2}'")

    def clean_dvd_vm(self, vmname):
        self.vmname = vmname
        self.execute.execute(cmd="sudo vboxmanage storageattach livedvd --storagectl " + "IDE " + "--port 1 --device 0 --type dvddrive --medium " + "emptydrive")

    def set_firmware_vm(self, vmname, firmware):
        self.vmname = vmname
        self.firmware = firmware
        self.execute.execute(cmd="sudo vboxmanage modifyvm " + self.vmname + " --firmware " + self.firmware)