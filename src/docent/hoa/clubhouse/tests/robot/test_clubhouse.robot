# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s docent.hoa.clubhouse -t test_clubhouse.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src docent.hoa.clubhouse.testing.DOCENT_HOA_CLUBHOUSE_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot src/plonetraining/testing/tests/robot/test_clubhouse.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a Clubhouse
  Given a logged-in site administrator
    and an add clubhouse form
   When I type 'My Clubhouse' into the title field
    and I submit the form
   Then a clubhouse with the title 'My Clubhouse' has been created

Scenario: As a site administrator I can view a Clubhouse
  Given a logged-in site administrator
    and a clubhouse 'My Clubhouse'
   When I go to the clubhouse view
   Then I can see the clubhouse title 'My Clubhouse'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add clubhouse form
  Go To  ${PLONE_URL}/++add++Clubhouse

a clubhouse 'My Clubhouse'
  Create content  type=Clubhouse  id=my-clubhouse  title=My Clubhouse


# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.title  ${title}

I submit the form
  Click Button  Save

I go to the clubhouse view
  Go To  ${PLONE_URL}/my-clubhouse
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a clubhouse with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the clubhouse title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
