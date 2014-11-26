Feature: As a curious user 
         I want to see a plot over gender distribution in Riksdagen
         So that I can see if the people are equally represented
         
    Scenario: There should be the correct elements.
        Given you browse to the "riksdagen" page
        Then The response should contain an element "svg#parliament_svg"
        Then The response should contain an element "div#parliament_mode_switcher"
        Then The response should contain an element "button#parliament_button"
        Then The response should contain an element "button#gender_button"

