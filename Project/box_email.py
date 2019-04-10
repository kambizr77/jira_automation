# -*- coding: utf-8 -*-
"""Module to send email using box's smtp server

This module is used to send email using Box's smtp server.

"""
import smtplib
import os

# Import the email modules we'll need
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from email.mime.text import MIMEText

class BoxEmail:
    """This class is used to send email.

    Furrently this class will only send emails that are test. This is the
    MIMEBase('text', 'plain').

    The class could be extended to other file types.


    """

    def __init__(self, to_addr, from_addr, subject,attachment):
        """
        Args:
            to_addr: To address for email
            from_addr: Who them email should be from
            subject: The subject of the email
            attachment: File to attach in email
        """
        self.to_addr = to_addr
        self.from_addr = from_addr
        self.attachment = attachment
        self.subject = subject

    def send_email(self,html):
        """Send the email"""
        # Create the container (outer) email message.
        msg = MIMEMultipart()
        msg['Subject'] = self.subject
        msg['From'] = self.from_addr
        msg['To'] = ','.join(self.to_addr)
        msg.preamble = self.subject
        # Open the file to attach to the email
        # with open(self.attachment) as f:
        #     lines=f.readlines()
        fp = open(self.attachment, 'rb')
        email_attachment = MIMEBase('text', 'plain')
        part2=part2 = MIMEText(html, 'html')
        email_attachment.set_payload(fp.read())
        fp.close()
        encode_base64(email_attachment)
        email_attachment.add_header('Content-Disposition', 'attachment',filename=self.attachment)
        msg.attach(email_attachment)
        msg.attach(part2)

        # Send the email via our own SMTP server.
        s = smtplib.SMTP('ext-mail.ve.box.net')
        s.sendmail(self.from_addr, self.to_addr, msg.as_string())
        s.quit()


def main():
    pass


if __name__ == '__main__':
    main()
