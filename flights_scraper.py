from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv



def scrapepage(driver, flights, review_url_list, writer, counter):
    for flight in flights:
        flight_dict={}

        try:
            airline_name= flight.find_element_by_xpath('.//div[@class="airlineName"]').text
            print(airline_name)
            flight_cost= flight.find_element_by_xpath('.//span[@class="viewDealPrice"]').text
            print(flight_cost)
            depart_time= flight.find_element_by_xpath('.//div[@class="departureDescription airportDescription"]').text
            print(depart_time)
        
        except:
            continue

        try:
            flight.find_element_by_xpath('.//span[@class="different"]')
            arrive_time= flight.find_element_by_xpath('.//div[@class="arrivalDescription airportDescription"]').text + flight.find_elements_by_xpath('./span[@class="different"]').text
        
        except:
            arrive_time= flight.find_element_by_xpath('.//div[@class="arrivalDescription airportDescription"]').text
            
        
        print(arrive_time)

        flight_duration= flight.find_element_by_xpath('.//div[@class="segmentDuration"]').text

        print(flight_duration)
        
        try:
            flight_flyscore= flight.find_element_by_xpath('.//span[@data-tooltip="light"]').text
            print(flight_flyscore)

        except:
            print('no flyscore')
            flight_flyscore='NA'
            pass

        
        driver.execute_script('scroll(0,{}*620)'.format(counter))
        counter += 1

        
        #find review tab and retrieve airline ratings
        try:
            
            flight.find_element_by_xpath('.//div[@class="toggleDetails showDetails"]').click()

            flight.find_element_by_xpath('.//li[@class="detailTab reviewsTab"]').click()
            
            wait_review= WebDriverWait(driver,10)
            wait_review.until(EC.presence_of_all_elements_located((By.XPATH,'.//div[@data-prwidget-name="common_bubble_rating"]/span')))

            airline_rating= flight.find_element_by_xpath('.//div[@class="ratingsSummary column"]/div[1]//span').get_attribute('alt')
            
            print(airline_rating)

            #retrieve html link 
            try:

                review_url= flight.find_element_by_xpath('.//div[@class="footer"]/a').get_attribute('href')
                
                #append  url in list
                review_url_list.append(review_url)
                
                                    
            except:
                review_url="NA"                                                           
                pass
                                
        
        except:
            airline_rating="NA"
            pass
        

        flight_dict['airline_name'] = airline_name
        flight_dict['flight_cost'] = flight_cost
        flight_dict['depart_time'] = depart_time
        flight_dict['arrive_time'] = arrive_time
        flight_dict['flight_duration'] = flight_duration
        flight_dict['flight_flyscore'] = flight_flyscore
        flight_dict['airline_rating'] = airline_rating
        flight_dict['review_url']= str(review_url)
        
        writer.writerow(flight_dict.values())







#flight scraper
def flightscraper(dates):


    begin_exec= time.time()

    # destinations( LA, Honolulu, San Francisco, Miami, Las Vegas)
    popular_dest= ['LAX', 'HNL', 'SFO', 'MIA', 'LAS']

    #dates= list(map(str,range(20171220, 20171232))) + list(map(str,range(20180101,20180120)))

    review_url_list=[]

    # getting all pages for each destination flights


    for date in dates:
        
        start_time_date=time.time()

        csv_file = open('flights{}.csv'.format(date), 'a')

        writer = csv.writer(csv_file, lineterminator = '\n')
        writer.writerow(['airline_name', 'flight_cost', 'depart_time', 'arrive_time', 'flight_duration', 'flight_flyscore','airline_rating', 'review_url'])
        
        for dest in popular_dest:

            start_time_dest= time.time()
            driver= webdriver.Chrome(r"C:\Users\hans\chromedriver.exe")
            url= "https://www.tripadvisor.com/CheapFlightsSearchResults-a_airport0.NYC-a_airport1.{}-a_date0.{}.html".format(dest,date) 
            
            print(url)

            driver.get(url)

            # Page index used to keep track of where we are.
            index = 1
            

            while True:
                    
                try:
                    print("Scraping Page number " + str(index))
                    index = index + 1
                    time.sleep(3)
                    
                    #find all flight entry information

                    wait_flights= WebDriverWait(driver,30)
                    
                    wait_flights.until(EC.presence_of_all_elements_located((By.XPATH,'.//div[@class="toggleDetails showDetails"]')))
                    
                    flights = driver.find_elements_by_class_name('entry')    

                    counter = 0

                    try:
                        scrapepage(driver, flights, review_url_list, writer, counter)
                    
                    except:
                        time.sleep(5)
                        flights = driver.find_elements_by_class_name('entry') 
                        scrapepage(driver, flights, review_url_list, writer, counter)



                    
                    #Locate button
                    wait_button = WebDriverWait(driver, 10)
                    button = wait_button.until(EC.element_to_be_clickable((By.XPATH,'//span[@class="nav next ui_button primary taLnk"]')))
                    
                    driver.execute_script("arguments[0].click();", button)

                        

                except Exception as e:
                    print(e)
                    driver.close()
                    break
                


            stop_time_dest= time.time()
            print("Time took {}: {} seconds".format(dest, stop_time_dest-start_time_dest))
        
        #close file after each date is finished
        csv_file.close()

        stop_time_date=time.time()
        print("Time took {}: {} seconds".format(date, stop_time_date-start_time_date))

    end_exec= time.time()

    print("Total time took {} seconds".format(end_exec-begin_exec))
    print('flight scrapper done')
    

    review_url_list=list(set(review_url_list))
    return(review_url_list)



#review scraper

def reviewscraper(dates):
    
    #open flights.csv file and scrape links
    
    unique_review_urls= flightscraper(dates)
    
    csv_file = open('review.csv', 'w')

    writer = csv.writer(csv_file, lineterminator = '\n')
    writer.writerow(['airline_name','legroom', 'seat_comfort', 'entertainment', 'customer_service', 'value_money', 'cleanliness','checkin_boarding', 'food_beverage'])
    

    index=1
    for url in unique_review_urls:
        
        try:
            print("Scraping url number " + str(index))
            time.sleep(3)
            
            review_dict={}

            review_driver= webdriver.Chrome(r"C:\Users\hans\chromedriver.exe")
            review_driver.get(url)


            
            airline_name= review_driver.find_element_by_class_name('heading_height').text

            review_summary=review_driver.find_element_by_class_name('barChart')

            legroom= review_summary.find_element_by_xpath('./li[1]/div[1]//span').get_attribute('alt')
            seat_comfort= review_summary.find_element_by_xpath('./li[1]/div[2]//span').get_attribute('alt')
            entertainment= review_summary.find_element_by_xpath('./li[2]/div[1]//span').get_attribute('alt')
            customer_service= review_summary.find_element_by_xpath('./li[2]/div[2]//span').get_attribute('alt')
            value_money= review_summary.find_element_by_xpath('./li[3]/div[1]//span').get_attribute('alt')
            cleanliness= review_summary.find_element_by_xpath('./li[3]/div[2]//span').get_attribute('alt')
            checkin_boarding= review_summary.find_element_by_xpath('./li[4]/div[1]//span').get_attribute('alt')
            food_beverage= review_summary.find_element_by_xpath('./li[4]/div[2]//span').get_attribute('alt')

            review_dict['airline_name']=airline_name
            review_dict['legroom']=legroom
            review_dict['seat_comfort']=seat_comfort
            review_dict['entertainment']=entertainment
            review_dict['customer_service']=customer_service
            review_dict['value_money']=value_money
            review_dict['cleanliness']=cleanliness
            review_dict['checkin_boarding']=checkin_boarding
            review_dict['food_beverage']=food_beverage
            
            writer.writerow(review_dict.values())
            
            print('review summary done for entry {}'.format(index))
            index+=1

            review_driver.close()  

        except:
            continue


    csv_file.close()