import base64
from datetime import date, datetime
from ..service import GoogleService
from .utils import make_message, make_label_dict, get_label_id
from .message import Message
from .label import Label
from .scopes import ReadonlyGmailScope
from .gmail_base import GmailBase
import os
import time
from datetime import datetime
import smtplib, ssl
from email.utils import getaddresses






class Gmail(GmailBase):


    def __init__(self, service: GoogleService or str = None, allow_modify: bool = True):
        if isinstance(service, GoogleService):
            self.service = service

        else:
            kwargs = {}
            if service:
                kwargs["session"] = service
            if not allow_modify:
                kwargs['scopes'] = [ReadonlyGmailScope()]
            self.service = GoogleService(api= "gmail", **kwargs)

        self.get_user()


    def __len__(self):
        return self.user.get("messagesTotal")


    def __str__(self):
        return f"email: {self.email_address}, scopes: {self.service.authenticated_scopes}"

    def get_user(self):
        self.user = self.service.users().getProfile(userId= "me").execute()


    @property
    def history_id(self):
        return self.user.get("historyId")


    @property
    def email_address(self):
        return self.user.get("emailAddress")


    def get_messages(
        self,
        label_ids: list or str = None,
        seen: bool = None,
        from_: str = None,
        after: date = None,
        before: date = None,
        label_name: str = None
        ):
        q = ""
        if not seen is None:
            if seen:
                q += "is:read"
            else:
                q += "is:unread"
        
        if after:
            q += f'after:{after.strftime("%Y/%m/%d")}'

        if before:
            q += f'before:{before.strftime("%Y/%m/%d")}'

        if from_:
            q += f"from:({from_})"

        if label_name:
            q += f"label:{get_label_id(label_name)}"
        if label_ids:
            if isinstance(label_ids, str):
                label_ids = [get_label_id(label_ids)]
            elif isinstance(label_ids, str):
                label_ids = list(map(get_label_id, label_ids))


        next_page_token = None
        messages, next_page_token = self._get_messages(next_page_token, label_ids, q)
        
        while True:
            try:
                message_id = next(messages)["id"]

            except StopIteration:
                if not next_page_token:
                    break
                messages, next_page_token = self._get_messages(next_page_token, label_ids, q)
                continue

            else:
                yield Message(self._get_message_raw_data(message_id), self)




    def get_message_by_id(self, message_id: str):
        raw_message = self._get_message_raw_data(message_id)
        return Message(raw_message, self)


    def handle_new_messages(self, func, handle_old_unread: bool = False, sleep: int = 3):
        history_id = self.history_id
        if handle_old_unread:
            msgs = self.get_messages('inbox', seen= False)
            for msg in msgs:
                func(msg)
        while True:
            print(f"Checking for messages - {datetime.now()}")
            data = self._get_history_data(history_id, ['messageAdded'], label_id= 'INBOX')
            historys = data.get("history")
            if historys:
                history_id = data['historyId']
                for history in historys:
                    messages = history.get('messages')
                    if messages:
                        for message in messages:
                            print("New message")
                            msg = self.get_message_by_id(message['id'])
                            func(msg)
            time.sleep(sleep)


    def send_message(
        self,
        to: list or str = None,
        subject: str = "", 
        text: str = None, 
        html: str = None, 
        attachments: list = [],
        cc: list or str = None,
        bcc: list or str = None,
        references: str = None,
        in_reply_to: str = None,
        thread_id: str = None
        ):
        message = make_message(self.email_address, to, cc, bcc, subject, text, html, attachments, references, in_reply_to)
        b64 = base64.urlsafe_b64encode(message).decode()
        body = {'raw': b64}
        if thread_id:
            body["threadId"] = thread_id
        data = self.service.message_service.send(userId= 'me', body= body).execute()
        return data



    def get_label_by_id(self, label_id):
            label_data = self._get_label_raw_data(label_id)
            return Label(label_data, self)



    def get_lables(self):
        labels_data = self._get_labels()
        for label in labels_data['labels']:
            yield self.get_label_by_id(label['id'])



    def create_label(
        self, 
        name: str,
        message_list_visibility,
        label_list_visibility,
        background_color: str = None,
        text_color: str = None
        ):

        body = make_label_dict(name= name, message_list_visibility= message_list_visibility, label_list_visibility= label_list_visibility, 
            background_color= background_color, text_color= text_color
            )

        data = self.service.labels_service.create(userId= 'me', body= body).execute()
        return self.get_label_by_id(data['id'])
