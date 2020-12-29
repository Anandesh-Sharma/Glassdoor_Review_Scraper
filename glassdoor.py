import csv
from pprint import pprint
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import pandas as pd


def sign_in(email, password):
    email_username = driver.find_element_by_id('userEmail')
    email_username.send_keys(email)

    email_pass = driver.find_element_by_id('userPassword')
    email_pass.send_keys(password)

    sign_in_button = driver.find_element_by_xpath(
        '/html/body/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div[3]/form/div[3]/div[1]/button')
    sign_in_button.click()
    return driver


def search_company(driver, company_name):
    select_company_option = driver.find_element_by_xpath('/html/body/header/nav[2]/div/div[1]/div[2]')
    select_company_option.click()
    try:
        select_company_option.click()
    except:
        pass
    c_name = driver.find_element_by_xpath(
        '/html/body/header/nav[1]/div/div/div/div[4]/div[3]/form/div/div[1]/div/div/input')
    c_name.send_keys(company_name)

    search_button = driver.find_element_by_xpath('/html/body/header/nav[1]/div/div/div/div[4]/div[3]/form/div/button')
    search_button.click()

    return driver


def extract_sub_stars(iHTML):
    soup = BeautifulSoup(iHTML, 'html5lib')
    subts = soup.findAll('div', attrs={'class': 'minor'})
    subss = soup.findAll('span', attrs={'class': 'subRatings__SubRatingsStyles__gdBars gdBars gdRatings med'})

    sub_dict = {}
    for subt, subs in zip(subts, subss):
        sub_dict[subt.text] = subs['title']

    return sub_dict


def extract_review(driver, index):
    base_x_path = '//*[@id="ReviewsFeed"]/ol/li'
    driver.find_element_by_xpath(base_x_path)
    try:
        review_date = driver.find_element_by_xpath(f'{base_x_path}[{index}]/div/div[1]/div/time').text
    except Exception:
        review_date = ''
    review_title = driver.find_element_by_xpath(f'{base_x_path}[{index}]/div/div[2]/div[2]/div[1]/h2/a').text
    review_stars = driver.find_element_by_xpath(
        f'{base_x_path}[{index}]/div/div[2]/div[2]/div[1]/div[1]/span/div[1]/div/div').text
    try:
        emp_info = driver.find_element_by_xpath(
            f'{base_x_path}[{index}]/div/div[2]/div[2]/div[1]/div[2]/div/span/span[1]').text
        emp_info = emp_info.split('-')
        emp_status = emp_info[0]
        emp_position = emp_info[1]
    except Exception:
        emp_position = None
        emp_status = None
    try:
        emp_loc = driver.find_element_by_xpath(
            f'{base_x_path}[{index}]/div/div[2]/div[2]/div[1]/div[2]/div/span/span[2]/span').text
    except Exception:
        emp_loc = None
        print(f'employee location not found in block {index}')
    try:
        continue_reading = driver.find_element_by_xpath(f'{base_x_path}[{index}]/div/div[2]/div[2]/div[2]/div[3]')
        continue_reading.click()
    except Exception:
        print(f'Continue not found in block {index}')
    main_text = driver.find_element_by_xpath(f'{base_x_path}[{index}]/div/div[2]/div[2]/div[1]/p').text
    pros_text = driver.find_element_by_xpath(f'{base_x_path}[{index}]/div/div[2]/div[2]/div[2]/div[1]/p[2]/span').text
    cons_text = driver.find_element_by_xpath(f'{base_x_path}[{index}]/div/div[2]/div[2]/div[2]/div[2]/p[2]/span').text
    try:
        advice_text = driver.find_element_by_xpath(
            f'{base_x_path}[{index}]/div/div[2]/div[2]/div[2]/div[3]/p[2]/span').text
    except Exception:
        advice_text = None
        print(f'advice text not found on block {index}')
    try:
        helpful_text = driver.find_element_by_xpath(
            f'{base_x_path}[{index}]/div/div[2]/div[2]/div[2]/div[5]/div[2]/div[1]/button').text
    except:
        helpful_text = driver.find_element_by_xpath(
            f'{base_x_path}[{index}]/div/div[2]/div[2]/div[2]/div[4]/div[2]/div[1]/button').text

    try:
        subs_html = driver.find_element_by_xpath(f"{base_x_path}[{index}]/div/div[2]/div[2]/div[1]/div[1]/span/div[2]")
        sub_stars = extract_sub_stars(subs_html.get_attribute('innerHTML'))
    except Exception as e:
        sub_stars = {}
        print(f'substars ain\'t present for this block {index}')

    review_dict = {
        'Review Date': review_date,
        'Employee Position': emp_position,
        'Employee Location': emp_loc,
        'Employee Status': emp_status,
        'Review Title': review_title,
        'Number of Helpful Votes': helpful_text,
        'Pros Text': pros_text,
        'Cons Text': cons_text,
        'Advice to Management': advice_text,
        'Review Stars': review_stars,
        'Employee Years at Company': main_text
    }
    if 'Work/Life Balance' not in sub_stars:
        sub_stars['Work/Life Balance'] = ''
    if 'Culture & Values' not in sub_stars:
        sub_stars['Culture & Values'] = ''
    if 'Diversity & Inclusion' not in sub_stars:
        sub_stars['Diversity & Inclusion'] = ''
    if 'Senior Management' not in sub_stars:
        sub_stars['Senior Management'] = ''
    if 'Compensation and Benefits' not in sub_stars:
        sub_stars['Compensation and Benefits'] = ''
    if 'Career Opportunities' not in sub_stars:
        sub_stars['Career Opportunities'] = ''
    final_dict = {**review_dict, **sub_stars}
    return final_dict


def get_all_reviews(driver, company_name):
    get_all_review = driver.find_element_by_xpath('//*[@class="moreBar"]')
    no_of_reviews = driver.find_elements_by_xpath('//*[@class="num h2"]')[1].text

    if no_of_reviews[-1:] == 'k':
        no_of_reviews = int(round(float(no_of_reviews[:-1]), 1) * 1000)
    else:
        no_of_reviews = int(no_of_reviews)

    get_all_review.click()

    # if the reviews are more than 10
    overall_rating = driver.find_element_by_css_selector(
        '.v2__EIReviewsRatingsStylesV2__ratingNum.v2__EIReviewsRatingsStylesV2__large').text
    if no_of_reviews % 10 == 0:
        iterations = no_of_reviews // 10
    else:
        iterations = no_of_reviews // 10 + 1

    try:
        if iterations == 1:
            for i in range(1, 11):
                data = extract_review(driver=driver, index=i)
                data['Overall Rating'] = overall_rating
                data['Company'] = company_name
                pprint(data)
                csv_writer(data)
        else:
            next_button = driver.find_element_by_xpath('//*[@class="pageContainer"]/button[7]')
            for k in range(iterations):
                for i in range(1, 11):
                    while True:
                        try:
                            data = extract_review(driver=driver, index=i)
                            break
                        except:
                            sleep(2)
                            print('Checking for the elements')
                    data['Overall Rating'] = overall_rating
                    data['Company'] = company_name
                    pprint(data)
                    csv_writer(data)
                    sleep(1)
                next_button.click()
                sleep(2)
    except Exception:
        import traceback
        traceback.print_exc()
        print('Reviews may be lower than 10 for this block or has no reviews')


def csv_writer(data):
    global is_created
    fieldnames = ['Company', 'Review Date', 'Employee Position', 'Employee Location', 'Employee Status',
                  'Review Title', 'Employee Years at Company', 'Number of Helpful Votes', 'Pros Text',
                  'Cons Text', 'Advice to Management', 'Work/Life Balance', 'Culture & Values',
                  'Diversity & Inclusion',
                  'Career Opportunities', 'Compensation and Benefits', 'Senior Management', 'Review Stars',
                  'Overall Rating']
    with open('review.csv', 'a+') as f:
        writer = csv.DictWriter(f, delimiter=',', lineterminator='\n', fieldnames=fieldnames)
        if not is_created:
            writer.writeheader()
            is_created = True

        writer.writerow({'Company': data['Company'], 'Review Date': data['Review Date'],
                         'Employee Position': data['Employee Position'], 'Employee Location': data['Employee Location'],
                         'Employee Status': data['Employee Status'], 'Review Title': data['Review Title'],
                         'Employee Years at Company': data['Employee Years at Company'],
                         'Number of Helpful Votes': data['Number of Helpful Votes'], 'Pros Text': data['Pros Text'],
                         'Cons Text': data['Cons Text'], 'Advice to Management': data['Advice to Management'],
                         'Work/Life Balance': data['Work/Life Balance'], 'Culture & Values': data['Culture & Values'],
                         'Diversity & Inclusion': data['Diversity & Inclusion'],
                         'Career Opportunities': data['Career Opportunities'],
                         'Compensation and Benefits': data['Compensation and Benefits'],
                         'Senior Management': data['Senior Management'],
                         'Review Stars': data['Review Stars'], 'Overall Rating': data['Overall Rating']})


if __name__ == "__main__":
    base_path = os.getcwd()
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1400x1000')
    options.add_argument('disable-gpu')
    driver = webdriver.Chrome(f'{base_path}/chromedriver', chrome_options=options)
    driver.set_window_size(1400, 1000)
    if not os.path.exists('review.csv'):
        is_created = False
    else:
        is_created = True
    """SIGN IN"""
    driver.get('https://www.glassdoor.co.in/profile/login_input.htm?userOriginHook=HEADER_SIGNIN_LINK')
    sign_in(email='anandeshsharma@gmail.com', password='Rock0004@')
    sleep(2)

    """COMPANY URL LIST"""
    company_url_list = pd.read_csv('links.csv')
    column = 'links'
    for index, row in company_url_list.iterrows():
        driver.get(row[column])
        company = driver.find_element_by_xpath('//*[@class="header cell info"]//span').text
        get_all_reviews(driver=driver, company_name=company)
        sleep(2)
