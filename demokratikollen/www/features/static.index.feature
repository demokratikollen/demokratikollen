Feature: Test the index static page.

  Scenario: There should be an index page
     Given You browse to the index page
     Then The page title should contain "Demokratikollen"

  Scenario: No header button should be activated
     Given You browse to the index page
     Then No header button should be activated