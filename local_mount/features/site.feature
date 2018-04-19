## -- FILE: features/example.feature
#Feature: Google Search Functionality
#    Scenario: can find search results Tolstanova
#        When visit url "http://www.google.com/ncr"
#        When field with name "q" is given "Tolstanova"
#        Then title becomes "Tolstanova - Google Search"
#        Then close
#
#
#    Scenario: can find search results Tolstanova Galyna
#        When visit url "http://www.google.com/ncr"
#        When field with name "q" is given "Tolstanova Galyna"
#        Then title becomes "Tolstanova Galyna - Google Search"
#        Then close
#
#    Scenario: can find search results Tolstanova Galyna -> www.drtolstanova.com
#        When visit url "http://www.google.com/ncr"
#        When field with name "q" is given "Tolstanova Galyna"
#        Then title becomes "Tolstanova Galyna - Google Search"
#        Then search site text "Толстанова Галина Александровна - Врач" and click
#        Then close
