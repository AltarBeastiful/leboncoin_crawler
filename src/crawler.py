#!/usr/bin/env python
# -*- coding: utf-8 -*-
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep

import requests
from lxml import html


class Ad(object):
    def __init__(self, ad_node):
        self._node = ad_node

    def url(self):
        return self._node.attrib['href']

    def title(self):
        return self._node.xpath("section/h2")[0].text.strip()


class Crawler(object):

    def __init__(self, url, email):
        self._url = url
        self._email = email
        self._seen = {}

    def crawl(self):
        while True:
            response = requests.get(self._url)

            if response.status_code != 200:
                print("Error status code : {}".format(response.status_code))

            page = html.fromstring(response.content)

            matching_ads = [Ad(ad_node=node) for node in page.xpath("//*[@id=\"listingAds\"]/section/section/ul/li/a")]
            print(matching_ads[0].title())

            new_ad_list = []
            for ad in matching_ads:
                ad_url = ad.url()
                if ad_url not in self._seen:
                    new_ad_list.append(ad)
                    self._seen[ad_url] = ad

            if new_ad_list:
                message = "{} new ads matching\n".format(len(new_ad_list))

                for ad in new_ad_list:
                    message += ad.title() + "\n" + ad.url() + "\n"

                print(message)
                self.send_mail(message)

            sleep(2)

    def send_mail(self, content):
        import smtplib

        gmailUser = 'legalizme@gmail.com'
        gmailPassword = ''

        msg = MIMEMultipart()
        msg['From'] = gmailUser
        msg['To'] = self._email
        msg['Subject'] = ""
        msg.attach(MIMEText(content))

        mailServer = smtplib.SMTP('smtp.gmail.com', 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmailUser, gmailPassword)
        mailServer.sendmail(gmailUser, self._email, msg.as_string())
        mailServer.close()

if __name__ == '__main__':
    c = Crawler(url="https://www.leboncoin.fr/locations/offres/ile_de_france/occasions/?mre=600&ros=2&roe=2&location=Strasbourg%2067000%2CStrasbourg%2067200%2CStrasbourg%2067100&f=p",
            email="r3m1.benoit@gmail.com")

    c.crawl()

