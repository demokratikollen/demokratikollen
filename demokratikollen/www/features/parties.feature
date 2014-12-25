Feature: Test the parties main page.

    Scenario: There should be an parties page with the correct button activated
        Given you browse to the "parties" page
        Then The page title should be "Partierna - Demokratikollen"
        But Only the header button "Partierna" should be activated

    Scenario: There should be the correct elements.
        Given you browse to the "parties" page
        Then The response should contain an element "svg"
        Then The response should contain an element ".line-marker"
        Then The response should contain an element ".line-path"
        Then The response should contain an element ".bar-rect"
        Then The response should contain an element ".click-rect"

