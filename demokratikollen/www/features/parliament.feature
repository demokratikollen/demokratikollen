Feature: As a curious user 
         I want to be able to look at different simple data from riksdagen in a nice way
         So that I can see who the members of riksdagen are.
    
    Scenario: Surfing the the riksdagen page should give you the correct page     
        Given you browse to the "riksdagen" page
        Then the page title should be "Riksdagen - Demokratikollen"
        But only the header button "Riksdagen" should be activated
        Then the response should contain an element "div#parliament_svg_div"
        Then the response should contain an element "div#parliament_date_slider div.date_slider"
    
    Scenario: Surfing to the index should give you a riksdagen plot.
        Given you browse to the "riksdagen" page
        Then wait for element "a.member_node" to appear
