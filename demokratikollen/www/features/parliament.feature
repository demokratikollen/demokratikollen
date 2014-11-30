Feature: As a curious user 
         I want to be able to look at different simple data from riksdagen in a nice way
         So that I can see who the members of riksdagen are.
    
    Scenario: Surfing the the riksdagen page should give you the correct page     
        Given you browse to the "riksdagen" page
        Then the page title should be "Riksdagen - Demokratikollen"
        But only the header button "Riksdagen" should be activated
        Then the response should contain an element "svg#parliament_svg"
        Then the response should contain an element "div#parliament_mode_switcher"
        Then the response should contain an element "button#parliament_button"
        Then the response should contain an element "button#gender_button"
    
    Scenario: Surfing to the index should give you a riksdagen plot.
        Given you browse to the "riksdagen" page
        Then wait for element "g.member_node.parliament" to appear

    Scenario: Surfing to the index and clicking on the gender button should give you a riksdagen plot.
        Given you browse to the "riksdagen" page
        And you click on the "button#gender_button" item
        Then wait for element "g.member_node.gender" to appear
        
