import luigi
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import requests
import os
import pandas as pd
import glob
from urllib.request import urlopen, urlretrieve, quote
from selenium.webdriver.chrome.options import Options

options = webdriver.ChromeOptions()
options.add_argument("download.default_directory=C:/Information-System/Semester-4/ADS/LendingClubData/")
driver = webdriver.Chrome(chrome_options=options)

class FetchURLTask(luigi.Task):
    def requires(self):
        pass

    def output(self):
        return luigi.LocalTarget('FetchURLTask.txt')

    def run(self):

        login = driver.get('https://www.lendingclub.com/auth/login')
        login_id = driver.find_element_by_name('email')
        password = driver.find_element_by_name('password')

        login_id.send_keys('deveshkandpal24@gmail.com')
        password.send_keys('devesh24')

        driver.find_element_by_css_selector('.form-button.form-button--submit').click()

        r = requests.get('https://www.lendingclub.com/account/summary.action')
        print (r.status_code)

        with self.output().open('w') as out_file:
            out_file.write('Done fetching url')

       # if r.status_code == 200:


class FetchDataTask(luigi.Task):

    def requires(self):
        return FetchURLTask()

    def output(self):
        return luigi.LocalTarget('FetchDataTask.txt')

    def run(self):
        output_path = 'C:/Information-System/Semester-4/ADS/LendingClubData/'

        page = driver.get('https://www.lendingclub.com/info/download-data.action')
        button = driver.find_element_by_id('currentLoanStatsFileName')

        select = Select(driver.find_element_by_id('loanStatsDropdown'))


        for element in select.options:
            element.click()
            print(element.get_attribute("text"))
            url = driver.find_element_by_id("currentLoanStatsFileName").get_attribute("href")
            split = url.rsplit('?', 1)[0]
            filename = os.path.join(output_path, split.rsplit('/', 1)[-1])
            button.click()
            print("Downloading %s to %s..." % (url, output_path))
            urlretrieve(url, filename)
            print(url)
        print("Done Fetching")


        with self.output().open('w') as out_file:
             out_file.write('Done fetching data')


class FetchDeclinedLoanDataTask(luigi.Task):

    def requires(self):
        return FetchURLTask()

    def output(self):
        return luigi.LocalTarget('FetchDeclinedLoanDataTask.txt')

    def run(self):
        output_path = 'C:/Information-System/Semester-4/ADS/LendingClubData/'

        page = driver.get('https://www.lendingclub.com/info/download-data.action')
        button = driver.find_element_by_id('currentRejectStatsFileName')

        select = Select(driver.find_element_by_id('rejectStatsDropdown'))


        for element in select.options:
            element.click()
            print(element.get_attribute("text"))
            url = driver.find_element_by_id("currentRejectStatsFileName").get_attribute("href")
            split = url.rsplit('?', 1)[0]
            filename = os.path.join(output_path, split.rsplit('/', 1)[-1])
            button.click()
            print("Downloading %s to %s..." % (url, output_path))
            urlretrieve(url, filename)
            print(url)
        print("Done Fetching")


        with self.output().open('w') as out_file:
             out_file.write('Done fetching reject loan data')

class DataToPandaFrame(luigi.Task):

    def requires(self):
        return FetchDataTask(), FetchDeclinedLoanDataTask()

    def run(self):

        path = 'C:/Information-System/Semester-4/ADS/LendingClubData/'

        allLoanStatsFile = glob.glob(path + "*LoanStats" + "*.zip")
        allRejectStatsFile = glob.glob(path + "*RejectStats" + "*.zip")
        loanStatsFrame = pd.DataFrame()
        rejectStatsFrame = pd.DataFrame()

        loanStatsDataFrame = []
        for f in allLoanStatsFile:
            df = pd.read_csv(f, compression='zip', low_memory='False', skiprows=[0])
            loanStatsDataFrame.append(df)
            loanStatsFrame = pd.concat(loanStatsDataFrame)

        loanStatsFrame.to_csv('outputLoanStats.csv', encoding='utf-8', index=False)

        rejectStatsDataFrame = []
        for f in allRejectStatsFile:
            df = pd.read_csv(f, compression='zip', low_memory='False', skiprows=[0])
            rejectStatsDataFrame.append(df)
            rejectStatsFrame = pd.concat(rejectStatsDataFrame)

            rejectStatsFrame.to_csv('outputRejectStats.csv', encoding='utf-8', index=False)

if __name__ == '__main__':

    luigi.run(["--lock-pid-dir", "C:\\temp\\", "--local-scheduler"], main_task_cls=DataToPandaFrame)
