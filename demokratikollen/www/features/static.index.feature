Feature: Test the index static page.

  Scenario: There should be an index page
     Given you browse to the index page
     Then The response be a page with the title "Demokratikollen - Hem"!

  Scenario: The correct header_button should be activated
     Given you browse to the index page
     Then The response should have only the "Hem" page button activated.