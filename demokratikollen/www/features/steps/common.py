from behave import *
from nose.tools import *
from selenium.common.exceptions import NoSuchElementException

@given('you browse to the "{page}" page')
def step_impl(context, page):
    if page == 'riksdagen':
      uri = 'riksdagen'
    context.driver.get("http://127.0.0.1:5555/" + uri)

@then('The response should contain an element "{css_selector}"')
def step_impl(context, css_selector):
    try:
        elements = context.driver.find_element_by_css_selector(css_selector)
    except NoSuchElementException:
        assert False, 'No element found'
    assert True