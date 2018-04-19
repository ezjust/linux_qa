# -- FILE: features/example.feature
Feature: Some tests for the local_mount utility
    Scenario: List recovery points of the agents
        When installed package "rapidrecovery-agent"
        Then list recovery points on the "10.10.61.30", user "login", password "pass", machine number "1"
        Then list recovery points on the "10.10.61.30", user "login", password "pass", machine name "10.10.38.233_d_c_2"

    Scenario: Mount of the recovery points for the agent
        When installed package "rapidrecovery-mono"
        Then mount recovery points of the "10.10.61.30", user "login", password "pass", machine number "7"

    Scenario: Mount of the recovery points for the agent with the name of the machine
        When installed package "rapidrecovery-mono"
        Then mount recovery points of the "10.10.61.30", user "login", password "pass", machine name "10.10.60.193"