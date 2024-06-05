from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import time
import base64
from datetime import datetime
from multiprocessing import Process

def get_month_name(month):
    month_names = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    return month_names[month]

def print_pdf(browser, application_number, day, month, year):
    pdf_data = browser.execute_cdp_cmd("Page.printToPDF", {
        "format": "A4",
        "printBackground": True
    })
    with open(f"scorecard_{application_number}_{year}_{month:02d}_{day:02d}.pdf", "wb") as f:
        f.write(base64.b64decode(pdf_data['data']))
    print(f"PDF saved successfully for {day}/{month}/{year}")
    return True

def check_print(browser, application_number, day, month, year):#check visibility of print button and proceed accordingly
    try:
        print_button = WebDriverWait(browser, 0.00001).until(
            EC.visibility_of_element_located((By.ID, "printPageButton"))
        )
        if print_button:
            print_pdf(browser, application_number, day, month, year)
            return True
        else:
            print(f"DOB {day}/{month}/{year} error {application_number}")
            return False
    except:
        return False

def close_intercepting_elements(browser):
    # Check & close intercepting elements (e.g., popups)
    try:
        intercepting_elements = browser.find_elements(By.CLASS_NAME, "swal2-container")
        if intercepting_elements:
            close_button = browser.find_element(By.XPATH, "//button[@type='button' and contains(@class, 'swal2-confirm')]")
            close_button.click()
    except:
        pass

def try_date(browser, application_number, day, month, year):
    try:
        close_intercepting_elements(browser)
        while True:
            try:
                applicationnumber = browser.find_element(By.ID, "scorecardmodel-applicationnumber")
                applicationnumber.clear()
                applicationnumber.send_keys(application_number)
            except:
                close_intercepting_elements(browser)
                if(check_print(browser, application_number, day-1, month, year)): 
                    return True
                print("application not found")
                continue
        
            day_select = browser.find_element(By.ID, "Day")
            day_select.send_keys(f"{day:02d}")
            
            month_value = get_month_name(month)
            month_select = browser.find_element(By.ID, "Month")
            month_select.send_keys(month_value) 
            
            year_select =browser.find_element(By.ID, "Year")
            year_select.send_keys(year)
            
            try:
                submit_button = browser.find_element(By.XPATH, "//button[@type='submit']")
                submit_button.click()
            except:
                close_intercepting_elements(browser)
                print("Couldnt submit")
                continue
        
            return check_print(browser, application_number, day, month, year)

    except Exception as e:
        print(f"Failed for {day}/{month}/{year}: {e}")
        return False

def download_scorecard(application_number, start_year, end_year):
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')  # Uncomment to run in headless mode
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    browser.get("https://neet.ntaonline.in/frontend/web/scorecard/index")
    time.sleep(0.1)  

    # Iterate over each year, month, and day within the specified range
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            for day in range(1, 32):
                try:
                    datetime(year, month, day)# Date Validity check
                except ValueError:
                    continue# Skip invalid dates
                
                if try_date(browser, application_number, day, month, year):
                    print(f"Scorecard found and saved for {day}/{month}/{year}")
                    browser.quit()
                    return

    browser.quit()
    print("No valid date found in the given range")


if __name__ == "__main__":
    processes = []
    a_num=[]#should contain application numbers 
    for i in range(len(a_num)):
        application_number = a_num[i]
        start_year = 2003
        end_year = 2006
        p = Process(target=download_scorecard, args=(application_number, start_year, end_year))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()
