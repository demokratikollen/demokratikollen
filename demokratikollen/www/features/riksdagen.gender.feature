Feature: As a curious user 
         I want to see a plot over gender distribution in Riksdagen
         So that I can see if the people are equally represented
         
  Scenario: There should be the correct elements.
     Given you browse to the "riksdagen" page
     Then The response should contain an element "svg#gender_svg"
     Then The response should contain an element "div#gender_div"