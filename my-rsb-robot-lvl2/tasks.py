from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    login()
    get_orders()
    archive_receipts()

def open_robot_order_website():
    """Opens the robot order website"""
    browser.goto("https://robotsparebinindustries.com/")

def login():
    """Logs in to the website
    Clicks order your robot tab"""
    page = browser.page()
    page.fill("#username", "maria")
    page.fill("#password", "thoushallnotpass")
    page.click("button:text('Log in')")
    page.click("a:text('Order your robot!')")

def get_orders():
    """Download the orders file.
    Read it as a table.
    Return the result"""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)
    table = Tables()
    rows = table.read_table_from_csv("orders.csv", header=True)

    for row in rows:
        print(row)
        close_annoying_modal()
        fill_the_form(row)

def close_annoying_modal():
    """Close the annoying modal"""
    page = browser.page()
    page.click("button:text('OK')")

def fill_the_form(order):
    """Fills out the form for ordering your robot"""
    page = browser.page()
    page.select_option("#head", order["Head"])
    page.check(f'input[type="radio"][value="{order["Body"]}"]')
    page.fill('input.form-control[type="number"][placeholder="Enter the part number for the legs"]', order["Legs"])
    page.fill("#address", order["Address"])
    page.click("button:text('Preview')")
    page.click("button:text('ORDER')")

    max_attempts = 5
    attempts = 0
    while page.is_visible("div.alert-danger") and attempts < max_attempts:
        page.click("button:text('ORDER')")
        attempts += 1
    
    store_receipt_as_pdf(order["Order number"])
    screenshot_robot(order["Order number"])
    embed_screenshot_to_receipt(order["Order number"])
    page.click("#order-another")
        
def store_receipt_as_pdf(order_number):
    """Store the receipt as a PDF file"""
    page = browser.page()
    html_receipt = page.locator("#receipt").inner_html()
    
    pdf = PDF()
    pdf.html_to_pdf(html_receipt, "output/"f"receipt_{order_number}.pdf")

def screenshot_robot(order_number):
    """Screenshot of the robot"""
    page = browser.page()
    screenshot_location = page.locator("#robot-preview")
    screenshot_location.screenshot(path="output/"f"robot_{order_number}.png")
    
def embed_screenshot_to_receipt(order_number):
    """Embed the screenshot into the PDF receipt"""
    pdf = PDF()
    screenshot_path = "output/"f"robot_{order_number}.png"
    pdf_path = "output/"f"receipt_{order_number}.pdf"
    list_of_files = [pdf_path, screenshot_path]
    pdf.add_files_to_pdf(
        files=list_of_files,
        target_document="output/"f"receipt_{order_number}.pdf"
    )

def archive_receipts():
    """Create ZIP archive of the receipts"""
    zip = Archive()
    zip.archive_folder_with_zip('output', 'output/receipts.zip', include='*.pdf')