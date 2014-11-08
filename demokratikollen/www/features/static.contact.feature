Feature: Test the contact static page.

  Scenario: There should be a contact page
     Given you browse to the contact page
     Then The response be a page with the title "Demokratikollen - Kontakt"!

  Scenario: The correct header_button should be activated
     Given you browse to the contact page
     Then The response should have only the "Kontakt" page button activated.