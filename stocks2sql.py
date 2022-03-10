import tkinter as tk
import pandas as pd
from tkinter import *
import six.moves.tkinter_ttk as ttk
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from requests_html import HTMLSession
import math
from time import sleep
from tqdm import tqdm

'''global variables for xpaths for the web scraping because yahoo finance periodically updates the website. If 
any of these throw an error, it's likely because its been tweaked on the website. There are still some hardcoded
 xpaths in the Screener class, but the ones here tend to cause the most trouble'''

# url for initial screening page
session = HTMLSession()
screener_url = 'https://finance.yahoo.com/screener/equity/new'

# Xpath links for interative buttons clicked by automated browser
sector_dropdown_xpath = '//*[@id="screener-criteria"]/div[2]/div[1]/div[1]/div[4]/div/div[1]/div[2]/ul/li/div/div'
med_cap_xpath = '//*[@id="screener-criteria"]/div[2]/div[1]/div[1]/div[2]/div/div[2]/div/button[2]'
large_cap_xpath = '//*[@id="screener-criteria"]/div[2]/div[1]/div[1]/div[2]/div/div[2]/div/button[3]'
execute_screener = '//*[@id="screener-criteria"]/div[2]/div[1]/div[3]/button[1]/span/span'

# two halves of a table taken from key-statistics page
financials_summary_lf_tbl = {"class": "Mb(10px) Pend(20px) smartphone_Pend(0px)"}
financials_summary_rt_tbl = {"class": "Pstart(20px) smartphone_PStart(0px)"}

# two halves of a table taken from quote summary page
quote_summary_lf_tbl = {"class": "D(ib) W(1/2) Bxz(bb) Pend(12px) Va(t) ie-7_D(i) smartphone_D(b) smartphone_W(100%) "
                                 "smartphone_Pend(0px) smartphone_BdY smartphone_Bdc($seperatorColor)"}
quote_summary_rt_tbl = {"class": "D(ib) W(1/2) Bxz(bb) Pstart(12px) Va(t) ie-7_D(i) ie-7_Pos(a) smartphone_D(b) "
                                 "smartphone_W(100%) smartphone_Pstart(0px) smartphone_BdB smartphone_Bdc("
                                 "$seperatorColor)"}


'''class containing entry boxes, checkboxes, and buttons for GUI. Also holds functions for what the GUI does
when the button is clicked. If entries are detected in the database information fields, the main function from
Screener class will run with 'sql=TRUE' and the optional parameter 'connection' filled, which is returned from the
'create_database_connection' field contained in this class'''


class ScreenerInput(tk.Frame):
    # init function inheriting from tkinter Frame
    def __init__(self, parent):
        super().__init__(parent)

        # SQL database input fields
        # Host label and field
        ttk.Label(self, text="Host:").grid(column=0, row=1, sticky=tk.W)
        self.host = ttk.Entry(self, width=30)
        self.host.focus()
        self.host.grid(column=1, row=1, sticky=tk.W)
        # User entry field
        ttk.Label(self, text="User:").grid(column=0, row=2, sticky=tk.W)
        self.user = ttk.Entry(self, width=30)
        self.user.focus()
        self.user.grid(column=1, row=2, sticky=tk.W)
        # password entry field
        ttk.Label(self, text="Password:").grid(column=0, row=3, sticky=tk.W)
        self.password = ttk.Entry(self, width=30)
        self.password.focus()
        self.password.grid(column=1, row=3, sticky=tk.W)
        # database entry field
        ttk.Label(self, text="Database:").grid(column=0, row=4, sticky=tk.W)
        self.database = ttk.Entry(self, width=30)
        self.database.focus()
        self.database.grid(column=1, row=4, sticky=tk.W)

        # list to hold sectors selected by user through checkboxes. Used in sector_button_clicked function
        self.active_sectors = []

        # IntVars for each sector name, stored in sectors_list in specific order to be called by indexing in
        # sector_button_clicked and used in Screener.main
        self.basicMaterial = IntVar(master=self, name="basicMaterial")
        self.consumerCyclical = IntVar(master=self, name="consumerCyclical")
        self.finanacialServices = IntVar(master=self, name="financialServices")
        self.realEstate = IntVar(master=self, name="realEstate")
        self.consumerDefensive = IntVar(master=self, name="consumerDefensive")
        self.healthcare = IntVar(master=self, name="healthcare")
        self.utilities = IntVar(master=self, name="utilities")
        self.communication = IntVar(master=self, name="communication")
        self.energy = IntVar(master=self, name="energy")
        self.industrials = IntVar(master=self, name="industrials")
        self.technology = IntVar(master=self, name="technology")
        self.analyze = IntVar(master=self, name="analyze")

        self.sectors_list = [self.basicMaterial, self.consumerCyclical, self.finanacialServices, self.realEstate,
                             self.consumerDefensive, self.healthcare, self.utilities, self.communication,
                             self.energy, self.industrials, self.technology]

        # label for checkbox instructions
        Label(self, text="Stock sectors to screen:").grid(row=5, column=0)

        # checkboxes. If checked returns a value of 1 to is_checked function
        Checkbutton(self, text="Basic Materials", variable=self.basicMaterial, onvalue=1, offvalue=0,
                    state=NORMAL, command=self.is_checked(self.basicMaterial)).grid(sticky=W, row=6, column=0)
        Checkbutton(self, text="Consumer Cyclical", variable=self.consumerCyclical, onvalue=1, offvalue=0,
                    command=self.is_checked(self.consumerCyclical)).grid(sticky=W, row=6, column=1)
        Checkbutton(self, text="Financial", variable=self.finanacialServices, onvalue=1, offvalue=0,
                    command=self.is_checked(self.finanacialServices)).grid(sticky=W, row=7, column=0)
        Checkbutton(self, text="Real Estate", variable=self.realEstate, onvalue=1, offvalue=0,
                    command=self.is_checked(self.realEstate)).grid(sticky=W, row=7, column=1)
        Checkbutton(self, text="Consumer Defensive", variable=self.consumerDefensive, onvalue=1, offvalue=0,
                    command=self.is_checked(self.consumerDefensive)).grid(sticky=W, row=8, column=0)
        Checkbutton(self, text="Health Care", variable=self.healthcare, onvalue=1, offvalue=0,
                    command=self.is_checked(self.healthcare)).grid(sticky=W, row=8, column=1)
        Checkbutton(self, text="Utilities", variable=self.utilities, onvalue=1, offvalue=0,
                    command=self.is_checked(self.utilities)).grid(sticky=W, row=9, column=0)
        Checkbutton(self, text="Communication", variable=self.communication, onvalue=1, offvalue=0,
                    command=self.is_checked(self.communication)).grid(sticky=W, row=9, column=1)
        Checkbutton(self, text="Energy", variable=self.energy, onvalue=1, offvalue=0, command=self.
                    is_checked(self.energy)).grid(sticky=W, row=10, column=0)
        Checkbutton(self, text="Industrials", variable=self.industrials, onvalue=1, offvalue=0,
                    command=self.is_checked(self.industrials)).grid(sticky=W, row=10, column=1)
        Checkbutton(self, text="Technology", variable=self.technology, onvalue=1, offvalue=0,
                    command=self.is_checked(self.technology)).grid(sticky=W, row=11, column=0)

        # Button to activate sector_button_clicked function
        self.btn = Button(self, text='Screen', state=ACTIVE, padx=20, pady=5)
        self.btn['command'] = self.sector_button_clicked
        self.btn.grid(sticky=E, row=11, column=1)

        for widget in self.winfo_children():
            widget.grid(padx=0, pady=5)

    # function to check values of checkboxes. If box checked, returns true. Used in iteration in sector_button_clicked
    @staticmethod
    def is_checked(button):
        # check if checkbox is clicked in gui, if yes return true
        if button.get() == 1:
            return True

    # establish server connection to sql database, uses database input fields. checks inputs for errors and improper
    # connections
    def create_server_connection(self):
        # reset server connection to None when called
        connection = None
        # list of string entries from database input fields
        database_info = [str(self.user.get()), str(self.host.get()), str(self.password.get()), str(self.database.get())]
        # database connection if only user and host is specified
        if database_info[2] == "" and database_info[3] == "":
            try:
                # create connection using mysql package
                connection = mysql.connector.connect(host=database_info[1],
                                                     user=database_info[0])
                # if connection is successful, prints message to console and returns connection at end of function
                print("MySQL connection successful")
            # error handling for improper connection
            except Error as err:
                # print which try statement error occured in for easier error tracing
                print(0)
                # print specific error from mysql.connector package
                print(f"Error: '{err}'")
                # if error = error number most frequent with this problem, print message box to user
                if err.errno == 1045:
                    messagebox.showinfo("Error", f"{err}. Recheck credentials to requested database")
        # database connection if password is not specified or needed for connection
        elif database_info[2] == "":
            try:
                connection = mysql.connector.connect(host=database_info[1],
                                                     user=database_info[0],
                                                     database=database_info[3])
                print("MySQL connection successful")
            except Error as err:
                print(1)
                print(f"Error: '{err}'")
                if err.errno == 1045:
                    messagebox.showinfo("Error", f"{err}. Recheck credentials to requested database")
        # database connection if database schema is not specified
        elif database_info[3] == "":
            try:
                connection = mysql.connector.connect(host=database_info[1],
                                                     user=database_info[0],
                                                     passwd=database_info[2])
                # message box to inform user that no database schema was provided, but process continues as normal
                messagebox.showinfo("Warning", "Connection to SQL server successful, but no schema has been identified")
            except Error as err:
                print(2)
                print(f"Error: '{err}'")
                if err.errno == 1045:
                    messagebox.showinfo("Error", f"{err}. Recheck credentials to requested database")
        else:
            # connection using all provided credentials
            try:
                connection = mysql.connector.connect(host=database_info[1],
                                                     user=database_info[0],
                                                     passwd=database_info[2],
                                                     database=database_info[3])
                print("MySQL connection successful")
            except Error as err:
                print(3)
                print(f"Error: '{err}'")
                if err.errno == 1049:
                    # message to ask user would like to create a database schema if one is not found under name provided
                    res = messagebox.askquestion("Error", "Database " + database_info[3] + " not found, do you wish to "
                                                                                           "create "
                                                                                           "new database schema " +
                                                 database_info[3] + "?")
                    if res == 'yes':
                        # creates new database with schema name
                        self.create_database(connection=mysql.connector.connect(host=database_info[1],
                                                                                user=database_info[0],
                                                                                passwd=database_info[2]),
                                             query=database_info[3])
                    elif res == 'no':
                        # returns to main app to allow user to retype credentials
                        messagebox.showinfo("info", "Returning to main app")
                elif err.errno == 1045:
                    messagebox.showinfo("Error", f"{err}. Recheck credentials to requested database")
        # returns connection to be optionally used in Screener.main
        return connection

    # function called when main button is clicked. Tallies checkboxes that are checked and appends the corresponding
    # sector_list index position to the empty list established earlier, active_sectors. Also checks if database entry
    # fields are filled to determine if a database connection needs to be made.
    def sector_button_clicked(self):
        # list of database input strings
        database_info = [str(self.user.get()), str(self.host.get()), str(self.password.get()), str(self.database.get())]
        # clear the empty active sectors list, just to be sure
        self.active_sectors.clear()
        # iterate through sectors_list that contains all possible sectors that could be checked
        for item in self.sectors_list:
            # check if the IntVar associated with the checkbox is checked using is_checked function.
            if ScreenerInput.is_checked(item) is True:
                # if so, append the index position from sectors_list and store it in active_sectors
                self.active_sectors.append(self.sectors_list.index(item))
        # check if all sql entry fields are empty (no database to connect to)
        if all([not x.strip() for x in database_info]):
            # if all fields are empty, call Screener.main with sql=False and no input for connection
            # will return collected results in a csv file
            Screener.main(self.active_sectors, sql=FALSE)
        else:
            # else, return sql=TRUE, return connection from create_server_connection as connection argument
            # calling now also serves to check if the input fields are correct
            Screener.main(self.active_sectors, sql=TRUE, connection=ScreenerInput.create_server_connection(self))

    # create database, used in one error handling situation in create_server_connection
    @staticmethod
    def create_database(connection, query):
        cursor = connection.cursor()
        command = "CREATE DATABASE " + query
        try:
            cursor.execute(command)
            print("DB created")
        except Error as err:
            print(f"Error: '{err}'")


'''Screener: class containing the functionality of the screener, given select inputs from ScreenerInput
Main function matches active sectors to input boxes on yahoo finance screener website.
checkbox selects those boxes using selenium and returns webpages with results, which it then scrapes ticker names from.
Fundamentals searches each ticker and scrapes the financial data from multiple web pages associated with ticker
returns csv or transports data to sql server'''


class Screener:
    # establish header to (hopefully) avoid getting IP banned
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/605.1.15 (KHTML, "
                             "like Gecko) Version/14.1.2 Safari/605.1.15"}

    '''add checkbox number of each sector from yahoo finance screener tool, checked using gui.py
    taken from gui list where index position corresponds to box ID number on yahoo finance tool'''
    merged_data = []

    @staticmethod
    def main(active_sectors, sql=bool, connection=None):
        box_ids = set()
        for item in active_sectors:
            if item == 0:
                box_ids.add(1)
            elif item == 1:
                box_ids.add(2)
            elif item == 2:
                box_ids.add(3)
            elif item == 3:
                box_ids.add(4)
            elif item == 4:
                box_ids.add(5)
            elif item == 5:
                box_ids.add(6)
            elif item == 6:
                box_ids.add(7)
            elif item == 7:
                box_ids.add(8)
            elif item == 8:
                box_ids.add(9)
            elif item == 9:
                box_ids.add(10)
            elif item == 10:
                box_ids.add(11)

        # open automated browser of yahoo finance screener using selenium. select predefined settings, plus the
        # ID boxes of sectors. Once list of stocks matching search criteria is compiled in the web browser
        # use beautifulSoup to parse out stock tickers and return as a list
        def checkbox(box_id):
            print("Loading automated browser to search Yahoo Finance")
            # establish web app to use. Had problems with safari
            driver = webdriver.Chrome()
            # url for stock screener on yahoo finannce website, defined above
            url = screener_url
            driver.maximize_window()
            # get current web page url
            driver.get(url)
            # TODO: LOW. resolve issue of cap buttons being selected without specified input, specifically small cap
            # small_cap = driver.find_element_by_xpath('//*[@id="screener-criteria"]/div[2]/div[1]/div[1]/div['
            #                                          '2]/div/div[2]/div/button[1]').click()
            # find elements by xpaths to be clicked
            med_cap = driver.find_element_by_xpath(med_cap_xpath)
            large_cap = driver.find_element_by_xpath(large_cap_xpath)
            sector_dropdown = driver.find_element_by_xpath(sector_dropdown_xpath)
            # click medium cap button
            med_cap.click()
            # click large cap button
            large_cap.click()
            # open sector dropdown to select individual sectors
            sector_dropdown.click()
            # wait for web page to catchup
            driver.implicitly_wait(3)
            sleep(5)
            # for every sector selected in gui, select here and wait 3 seconds between each
            driver.find_element_by_xpath(
                '//*[@id="dropdown-menu"]/div/div[2]/ul/li[' + str(box_id) + ']/label/span').click()
            sleep(5)
            # find button to run screener on yahoo finance
            execute_btn = driver.find_element_by_xpath(execute_screener)
            # click button
            execute_btn.click()
            # wait for new web page to be loaded
            sleep(5)
            driver.implicitly_wait(5)
            # restablish url variable as the current url holding the results of the screening
            url = driver.current_url
            # quit out of automated browser
            driver.quit()
            # establish empty list for company codes
            company_code = []

            # loop through resulting webpage of selected stocks using bs4 and pull tickers into company code list
            print("Collecting company names...")
            # establish beautiful soup session to parse html
            ticker_est = session.get(url, headers=Screener.headers, timeout=5).text
            est_soup = bs(ticker_est, 'html.parser')
            # find estimated number of stocks returned by screener to know how many return pages there will be
            # 100 stocks per page
            ticker_number = est_soup.find('div', attrs={'class': 'Fw(b) Fz(36px)'})
            rounded_ticker = int(math.ceil(int(ticker_number.getText()) / 100.0)) * 100
            # find estimated tickers for use in tqdm search range
            for i in tqdm(range(0, rounded_ticker, 100), position=0):
                index = url.find('dependentField')
                # different web page url needed for each page holding stock tickers
                final_url = url[:index] + 'count=100&' + url[index:] + '&offset=' + str(i)
                print(final_url)
                # establish beautiful soup session to parse html of each return page
                response = session.get(final_url, headers=Screener.headers, timeout=5).text
                html_soup = bs(response, 'html.parser')
                # html tag holding company names
                for companies in html_soup.find_all('a', attrs={'class': 'Fw(600) C($linkColor)'}):
                    # return text of company names
                    company_code.append(companies.text)
            print(company_code)
            # return list of company names (tickers) for use in other functions
            return company_code

        # for each company name returned, go to web page for company and scrape financial data
        def fundamentals(companies):
            # empty list to store dictionaries that will hold financial metrics for all stocks
            dataset = []
            i = 0
            for symbol in companies:
                # scrape statistics page using beautiful soup
                fund_url = "https://finance.yahoo.com/quote/" + symbol + "/key-statistics?p=" + symbol
                fund_response = session.get(fund_url, headers=Screener.headers, timeout=5).text
                fund_html_soup = bs(fund_response, 'html.parser')
                # financials1 is left table from statistics page
                financials1 = fund_html_soup.find("div", attrs=financials_summary_lf_tbl)
                # return text values from table without html code, "key, value" pairs stored subsequently in list
                raw_financials1 = [texts.text for texts in financials1.find_all("td")]
                # take "Key, value" pairs stored next to each other in previous list and put in dictionary
                statistics1 = {key: value for key, value in zip(raw_financials1[::2], raw_financials1[1::2])}
                # financials2 is right table
                financials2 = fund_html_soup.find("div", attrs=financials_summary_rt_tbl)
                # return text values from table without html code, "key, value" pairs stored subsequently in list
                raw_financials2 = [texts.text for texts in financials2.find_all("td")]
                # take "Key, value" pairs stored next to each other in previous list and put in dictionary
                statistics2 = {key: value for key, value in zip(raw_financials2[::2], raw_financials2[1::2])}
                # add company ticker for identification
                statistics1["Ticker"] = symbol

                # function to merge two dictionaries
                def merge(dict1, dict2):
                    res = {**dict1, **dict2}
                    return res

                # join two tables (stored as dicts) from financial statistics using merge function
                fin_statistics = merge(statistics1, statistics2)

                # pull basic info from quote summary page for each stock using beautiful soup
                quote_url = "https://finance.yahoo.com/quote/" + symbol + "?p=" + symbol
                quote_response = session.get(quote_url, headers=Screener.headers, timeout=5).text
                quote_html_soup = bs(quote_response, 'html.parser')
                # left half of table
                basics1 = quote_html_soup.find("div", attrs=quote_summary_lf_tbl)
                # right half of table
                basics2 = quote_html_soup.find("div", quote_summary_rt_tbl)
                # return text values from table without html code, "key, value" pairs stored subsequently in list
                basics_text1 = [texts.text for texts in basics1.find_all("td")]
                # take "Key, value" pairs stored next to each other in previous list and put in dictionary
                basic_dict1 = {key: value for key, value in zip(basics_text1[::2], basics_text1[1::2])}
                # return text values from table without html code, "key, value" pairs stored subsequently in list
                basics_text2 = [texts.text for texts in basics2.find_all("td")]
                # take "Key, value" pairs stored next to each other in previous list and put in dictionary
                basic_dict2 = {key: value for key, value in zip(basics_text2[::2], basics_text2[1::2])}
                # join two tables (stored as dicts) from quote summary page using merge function
                basic_statistics = merge(basic_dict1, basic_dict2)
                # get current price
                current_price = quote_html_soup.find("fin-streamer",
                                                     attrs={"class": "Fw(b) Fz(36px) Mb(-4px) D(ib)"})
                # add current price to dictionary unless unavailable for whatever reason
                try:
                    fin_statistics["Current price"] = current_price.getText()
                except AttributeError:
                    fin_statistics["Current price"] = "N/A"
                # merge both dictionaries into larger dictionary using merge function
                joined_dict = merge(fin_statistics, basic_statistics)
                # append dict for each stock to a larger dataset
                dataset.append(joined_dict)
                # take out for final product
                i = i + 1
                if i > 3:
                    break
            # turn dataset (list of dicts) to pandas datatable
            datatable = pd.DataFrame(dataset)
            return datatable
        # if sql is false (no sql info input into gui) return scraped data as a stored csv
        if sql is False:
            for ID in box_ids:
                fundamentals(checkbox(ID))
        #             return csv
        # else add to sql database table
        else:
            for ID in box_ids:
                fundamentals(checkbox(ID)).to_sql("STOCKS", con=connection, if_exists='append')


'''GUI: class to display GUI with ScreenerInput as widgets within gui'''


class GUI(tk.Tk):
    # init function holding title and size of GUI window
    def __init__(self):
        super().__init__()
        self.title("Stock Screener to SQL")
        self.resizable(0, 0)
        self.__create_widgets()

    # function to create widgets and store them inside of GUI window
    def __create_widgets(self):
        input_frame = ScreenerInput(self)
        input_frame.pack(fill="both", expand=True)


# when script is called display GUI
if __name__ == "__main__":
    gui = GUI()
    gui.mainloop()
