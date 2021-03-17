from datetime import datetime
import os
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
from urllib.parse import urljoin
import numpy as np
import pathlib



class Webpage:
  def __init__(self, base_url, date_range):
      self.base_url = base_url
      self.date_range = date_range


  def get_url(self):
      date_range_list = self.date_range.split("-")
      start_date_object = datetime.strptime(date_range_list[0], '%d %b %Y')
      end_date_object = datetime.strptime(date_range_list[1], '%d %b %Y')
      start_date = start_date_object.strftime("%Y-%m-%d")
      end_date = end_date_object.strftime("%Y-%m-%d")
      url_ext="?sc_lang=en&DateFrom="+start_date+ "&DateTo="+end_date\
              +"&Category=&Category2="
      url = urljoin(self.base_url,url_ext )

      return url


  def get_page(self):
      url= self.get_url()
      driver = webdriver.Chrome(ChromeDriverManager().install())
      driver.get(url)
      time.sleep(2)
      scroll_pause_time = 2
      screen_height = driver.execute_script("return window.screen.height;")
      i = 1
      while True:
          # scroll one screen height each time
          driver.execute_script("window.scrollTo(0, {screen_height}*{i});"
                                .format(screen_height=screen_height, i=i))
          i += 1
          time.sleep(scroll_pause_time)
          # update scroll height each time after scrolled, as the scroll height
          # can change after we scrolled the page
          scroll_height = driver.execute_script("return document.body."
                                                "scrollHeight;")
          # Break the loop when the height we need to scroll to is larger
          # than the total scroll height
          if (screen_height) * i > scroll_height:
              break
      try:
          html_page = BeautifulSoup(driver.page_source, "html.parser")
      except:
          raise Exception(
              '{Status:Failure Remark:Not able to fetch the html page}')

      return html_page


  def download_pdf(self):
      html_page=self.get_page()
      notification_div = html_page.find_all('div',
                                            {'class': 'whats_on_tdy_text_2'})
      total_notification=len(notification_div)

      downloaded_status = []
      for index1 in range(total_notification):
          downloaded_status.append(['None', 'None'])
      downloaded_status = np.array(downloaded_status)

      main_url_list=[]
      appendix_url_list = []

      parsed_uri = urlparse(self.base_url)
      root_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

      for i in range(total_notification):
          a_tag = notification_div[i].find('a')
          link = root_url + a_tag.get('href')
          title = str(i) + a_tag.contents[0]
          title = title.replace('/', ',')
          main_url_list.append(link)
          appendix = notification_div[i].nextSibling.find_all('a')
          appendix_dict = {}
          appendix_url_sublist=[]

          for count in range(len(appendix)):
              appendix_dict[appendix[count].contents[0]] = appendix[count].get(
                                                           'href')
              appendix_url_sublist.append(root_url+appendix[count].get('href'))
              # dict created of appendix file {title:link}
          appendix_url_list.append(appendix_url_sublist)

          # download the main pdf file
          try:
              response = requests.get(link)
              file_path = title
              if not os.path.exists(file_path):
                  os.makedirs(file_path)
              with open(title + "/" + title + ".pdf", 'wb') as f:
                  f.write(response.content)
              downloaded_status[i][0] = 'Done'
          except:
              downloaded_status[i][0]= 'Fail'

          # download the appendix pdf file
          try:
              for key in appendix_dict:
                  response_extra = requests.get(root_url
                                                + appendix_dict[key])
                  with open(title + "/" + key + ".pdf", 'wb') as f:
                      f.write(response_extra.content)
                      downloaded_status[i][1] = 'Done'
          except:
            downloaded_status[i][1] = 'Fail'
      #in downloaded_status each index correspond to a file no
      #at each index [0] element correpond to status of main file
      #at each index [1] element correpond to status of appendix file
      self.completion_message(downloaded_status,main_url_list,appendix_url_list)


  def completion_message(self,downloaded_status,main_url_list,appendix_url_list):
      if not(any("Fail" in sublist for sublist in downloaded_status)):
          print('Status: Success')
          print()
          print('Location of downloaded file:'+str(pathlib.Path(__file__).
                                                   parent.absolute()))
      else:
          failed_file = np.where(downloaded_status == 'Fail')
          failed_file = np.asarray(failed_file).T

          success_file = np.where(downloaded_status == 'Done')
          success_file = np.asarray(success_file).T

          fail_message=[]
          success_message=[]

          for t in failed_file:
              if(t[1]==0):
                  fail_message.append(
                      'File no ' + str(t[0]) + ' main pdf not able to download'
                      +' link '+str(main_url_list[t[0]]) )
              elif(t[1]==1):
                  fail_message.append(
                      'File no ' + str(t[0])
                      + ' appendix pdf not able to download'+ ' link '
                      +str(appendix_url_list[t[0]]))

          for t in success_file:
              if(t[1]==0):
                  success_message.append(
                      'File no '+ str(t[0]) + ' main pdf successfully download'
                      +' link '+str(main_url_list[t[0]]))
              elif(t[1]==1):
                  success_message.append(
                      'File no ' + str(t[0])
                      + ' appendix pdf successfully download'
                      + ' link '+str(appendix_url_list[t[0]]))

          fail_message = "\n".join(fail_message)
          success_message = "\n".join(success_message)

          print('Status:Failure')
          print()
          print('List of files not able to download')
          print(fail_message)
          print()
          print('List of successfully  downloaded files')
          print(success_message)
          print()
          print('Location of succesfully downloaded file: '
                +str(pathlib.Path(__file__).parent.absolute()))
























