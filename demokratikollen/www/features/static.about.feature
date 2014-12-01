Feature: Test the about static page.

  Scenario: There should be an about page
     Given You browse to the about page
     Then The page title should be "Om Demokratikollen"

  Scenario: No header button should be activated
     Given You browse to the about page
     Then No header button should be activated