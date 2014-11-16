from behave import *
from nose.tools import *

@given('you browse to the index page')
def step_impl(context):
    context.driver.get("http://127.0.0.1:5555/")
    eq_(context.driver.title.startswith('Demokratikollen'), True)

@given('you browse to the contact page')
def step_impl(context):
    context.driver.get("http://127.0.0.1:5555/kontakt")
    eq_(context.driver.title.startswith('Demokratikollen'), True)

@then('The response be a page with the title "{title}"!')
def step_impl(context, title):
    eq_(context.driver.title, title)

@then('The response should have only the "{button_title}" page button activated.')
def step_impl(context, button_title):
    elements = context.driver.find_elements_by_css_selector('div.header li')

    for element in elements:
       if button_title in element.get_attribute('innerHTML'):
          eq_(element.get_attribute('class'), 'active')
       else:
          ok_(element.get_attribute('class') != 'active', 'More than one header icon active')




