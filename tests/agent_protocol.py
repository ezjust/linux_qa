from __future__ import print_function
from my_utils.system import *



class AgentProtocol(Agent):

    default_protocol = "sudo echo YES | openssl s_client -connect localhost:8006 | grep TLSv1.2"
    tls1_2 = "echo YES | openssl s_client -connect localhost:8006 -tls1_2"
    tls1_1 = "echo YES | openssl s_client -connect localhost:8006 -tls1_1"
    tls1 = "echo YES | openssl s_client -connect localhost:8006 -tls1"
    sslv2 = "sudo openssl s_client -connect localhost:8006 -ssl2"
    sslv3 = "sudo openssl s_client -connect localhost:8006 -ssl3"
    dtls1 = "sudo openssl s_client -connect localhost:8006 -dtls1"



    def __init__(self):
        super(Repoinstall, self).__init__()

    def setUp(self):
        self.install_agent_fromrepo()

    def tearDown(self):
        self.uninstall_agent()


    def runTest(self):

        self.check_agent_is_running()

        if self.execute.error_code(self.default_protocol) is not 0:
            raise Exception("%s return not '0' error code. This protocol should"
                             "not be used" % self.default_protocol)# TLS1_2 should be used by default

        if self.execute.error_code(self.tls1_1) is not 0:
            raise Exception(
                "%s return not '0' error code. This protocol should"
                "not be used" % self.tls1_1)  # TLS1_1 should be available for using

        if self.execute.error_code(self.tls1_2) is not 0:
            raise Exception(
                "%s return not '0' error code. This protocol should"
                "not be used" % self.tls1_2)  # TLS1_2 should be available for using

        if self.execute.error_code(self.tls1) is not 1:
            raise Exception(
                "%s return not '0' error code. This protocol should"
                "not be used" % self.tls1)  # TLS1 should NOT be available for using

        if self.execute.error_code(self.sslv2) is not 1:  # sslv2 should NOT be available for using
            raise Exception("%s return not '1' error code. This protocol should"
                            "not be used" % self.sslv2)

        if self.execute.error_code(self.sslv3) is not 1:  # sslv3 should NOT be available for using
            raise Exception("%s return not '1' error code. This protocol should"
                            "not be used" % self.sslv3)

        if self.execute.error_code(self.dtls1) is not 1:  # dtls1 should NOT be available for using
            raise Exception("%s return not '1' error code. This protocol should"
                            "not be used" % self.dtls1)



###
 #Testing protocols (via sockets except TLS 1.2, SPDY+HTTP2)

 #SSLv2               not offered (OK)
 #SSLv3               not offered (OK)
 #TLS 1               not offered
 #TLS 1.1             offered
 #TLS 1.2             offered (OK)
 #Version tolerance   downgraded to TLSv1.2 (OK)
 #SPDY/NPN            not offered
 #HTTP2/ALPN          not offered

###