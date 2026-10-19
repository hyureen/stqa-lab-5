"""Lab 5: automate login, create a task, mark it complete, log out.

Run with:
    pytest test_ui.py -v --html=report.html --self-contained-html
"""
import uuid

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.login_page import LoginPage
from pages.task_page import NewTaskPage, TaskListPage

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo1234"


def wait_for_logged_in(driver):
    """After clicking Log in, wait for the new-task form to appear.
    This proves login worked, and makes sure the session cookie is set
    before the test navigates anywhere else."""
    return WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(NewTaskPage.TITLE_INPUT)
    )


def test_login_with_valid_credentials(driver, base_url):
    login_page = LoginPage(driver, base_url)
    login_page.open()
    login_page.login(DEMO_USERNAME, DEMO_PASSWORD)

    title_input = wait_for_logged_in(driver)
    assert title_input.is_displayed()
    assert "/login" not in driver.current_url


def test_login_with_invalid_credentials(driver, base_url):
    login_page = LoginPage(driver, base_url)
    login_page.open()
    login_page.login("demo", "wrong-password")
    error = login_page.wait_for_error()
    assert "Invalid username or password" in error.text


def test_create_task(driver, base_url):
    login_page = LoginPage(driver, base_url)
    login_page.open()
    login_page.login(DEMO_USERNAME, DEMO_PASSWORD)
    wait_for_logged_in(driver)

    new_task_page = NewTaskPage(driver, base_url)
    new_task_page.open()
    new_task_page.create_task(
        title="Prepare slides", priority="2", due_date="2026-12-01", hours="3"
    )

    banner = new_task_page.wait_for_success()
    assert banner.is_displayed()


def test_mark_task_complete_and_logout(driver, base_url):
    login_page = LoginPage(driver, base_url)
    login_page.open()
    login_page.login(DEMO_USERNAME, DEMO_PASSWORD)
    wait_for_logged_in(driver)

    new_task_page = NewTaskPage(driver, base_url)
    new_task_page.open()
    # Unique title, so we can find our own task among other groups' tasks
    title = f"Finish lab report {uuid.uuid4().hex[:8]}"
    new_task_page.create_task(
        title=title, priority="1", due_date="2026-12-05", hours="2"
    )
    new_task_page.wait_for_success()

    task_list_page = TaskListPage(driver, base_url)
    task_list_page.open()

    task_id = task_list_page.find_task_id(title)
    task_list_page.mark_complete(task_id)
    assert task_list_page.wait_until_completed(task_id)
    assert "Completed" in driver.find_element(*TaskListPage.status_cell(task_id)).text

    task_list_page.logout()
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(LoginPage.USERNAME_INPUT)
    )
    assert "/login" in driver.current_url
