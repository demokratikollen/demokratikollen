Feature: Test the parties main page.

  Scenario: There should be an parties page with the correct button activated
     Given You browse to the parties page
     Then The page title should be "Partierna - Demokratikollen"
     But Only the header button "Partierna" should be activated
