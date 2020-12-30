#uvicorn main:app --reload

import os
import sys
import selenium
from fastapi import FastAPI,HTTPException, Response
from http import HTTPStatus
from typing import Optional
from random import randint
from time import sleep
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

USERNAME=os.getenv('PROVIDER_PORTAL_USERNAME', 'NOT FOUND')
PASSWORD=os.getenv('PROVIDER_PORTAL_PASSWORD', 'NOT FOUND')
PROVIDER_PORTAL_URL=os.getenv('PROVIDER_PORTAL_URL', 'NOT FOUND')
DRIVER_ELEMENT_WAIT_TIME_IN_SEC=20
DRIVER_EXECUTOR=os.getenv('DRIVER_EXECUTOR', 'NOT FOUND')

class ProviderPortalBase():
    
    def __init__(self):
        
        #need options for remote execution
        caps = {'browserName': os.getenv('BROWSER', 'firefox')}
        self.driver = webdriver.Remote(command_executor=DRIVER_EXECUTOR,desired_capabilities=caps)
        #local driver
        #self.driver = webdriver.Firefox()
        self.driver.get(PROVIDER_PORTAL_URL)
        self.login()
  
    def tearDown(self):
        # cleanup
        #self.driver.close()
        self.driver.quit()
        print('Driver closed browser')
        
    def login(self):
        HOMEPAGE_USERNAME_TEXTBOX=(By.ID, "asPrimary_ctl00_txtLoginId")
        HOMEPAGE_PASSWORD_TEXTBOX=(By.ID, "asPrimary_ctl00_txtPassWord")
        HOMEPAGE_SUBMIT_BUTTON=(By.ID, "asPrimary_ctl00_btnSubmit")

        self.enter_text(HOMEPAGE_USERNAME_TEXTBOX,USERNAME)
        self.enter_text(HOMEPAGE_PASSWORD_TEXTBOX,PASSWORD)
        self.click(HOMEPAGE_SUBMIT_BUTTON)

        #accept terms and condtions

        TERMSPAGE_AGREE_BUTTON=(By.ID, "asPrimary_ctl00_cmdAgreeContinue")

        self.click(TERMSPAGE_AGREE_BUTTON)
        
    # this function performs click on web element whose locator is passed to it.
    def click(self,by_locator):
        WebDriverWait(self.driver, DRIVER_ELEMENT_WAIT_TIME_IN_SEC).until(EC.visibility_of_element_located(by_locator)).click()
    
    # this function asserts comparison of a web element's text with passed in text.
    def assert_element_text(self,by_locator, element_text):
        web_element=WebDriverWait(self.driver, DRIVER_ELEMENT_WAIT_TIME_IN_SEC).until(EC.visibility_of_element_located(by_locator))
        assert web_element.text == element_text

    # this function performs text entry of the passed in text, in a web element whose locator is passed to it.
    def enter_text(self,by_locator, text):
        return WebDriverWait(self.driver, DRIVER_ELEMENT_WAIT_TIME_IN_SEC).until(EC.visibility_of_element_located(by_locator)).send_keys(text)

    # this function checks if the web element whose locator has been passed to it, is enabled or not and returns
    # web element if it is enabled.
    def is_enabled(self,by_locator):
        return WebDriverWait(self.driver, DRIVER_ELEMENT_WAIT_TIME_IN_SEC).until(EC.visibility_of_element_located(by_locator))

    # this function checks if the web element whose locator has been passed to it, is visible or not and returns
    # true or false depending upon its visibility.
    def is_visible(self,by_locator):
        element=WebDriverWait(self.driver, DRIVER_ELEMENT_WAIT_TIME_IN_SEC).until(EC.visibility_of_element_located(by_locator))
        return bool(element)

class OrderHistory(ProviderPortalBase):
    
    def orderHistorySearch(self):
        PORTAL_HOME_ORDER_HISTORY_LINK = (By.ID, "asSearch_ctl00_LnbOrderHistory")
        ORDER_HISTORY_SHOW_ME=(By.ID, "asPrimary_ctl00_RbMyOrders")
        ORDER_HISTORY_TYPE=(By.ID, "asPrimary_ctl00_RbDiagnosticImaging")
        ORDER_HISTORY_TIMEFRAME=(By.XPATH,"//select[@id='asPrimary_ctl00_DdlWithin']/option[@value='90']") #90 days
        ORDER_HISTORY_ORDER_STATUS=(By.XPATH,"//select[@id='asPrimary_ctl00_DdlStatusMyOrdersRbm']/option[@value='']")  #all
        ORDER_HISTORY_GO_BUTTON=(By.ID, "asPrimary_ctl00_BtnSearch")
        ORDER_HISTORY_NO_RESULTS_MSG=(By.XPATH,"//div[@id='vsMessages' and contains(text(),'No Results Found.')]")

        self.click(PORTAL_HOME_ORDER_HISTORY_LINK)
        self.click(ORDER_HISTORY_SHOW_ME)
        self.click(ORDER_HISTORY_TYPE)
        self.click(ORDER_HISTORY_TIMEFRAME)
        self.click(ORDER_HISTORY_ORDER_STATUS)
        self.click(ORDER_HISTORY_GO_BUTTON)
        if self.is_visible(ORDER_HISTORY_NO_RESULTS_MSG):
            print('No Results Found')
            return None
     

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Not a lot here right now. Try /orderhistory"}

@app.get("/orderhistory/", status_code=200)
def order_history():
    try:
        myOrderHistory=OrderHistory()
        results = myOrderHistory.orderHistorySearch()
        myOrderHistory.tearDown()
        if results is None:
            return Response(status_code=HTTPStatus.NO_CONTENT.value)
        return results
    except Exception as e:
        print('ERROR: ', e)
        if myOrderHistory:
            myOrderHistory.tearDown()
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="{e}")

