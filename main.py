import os
import pickle
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from datetime import datetime
from db_ops import DB_Connections
import json

# The scopes required for GMail API access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# The file path to store the token (to avoid authorization every time)
TOKEN_FILE = 'token.pickle'


RULES = json.load(open('rules.json', 'r'))


class EmailFetcher:

    @staticmethod
    def authenticate():
        creds = None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)

        return creds

    @staticmethod
    def format_email_data(msg):
        email_details = {}
        email_details['snippet'] = msg['snippet']
        for obj in msg['payload']['headers']:
            if obj['name'] == 'Reply-To':
                email_details['sender'] = obj['value']
            if obj['name'] == 'Delivered-To':
                email_details['receiver'] = obj['value']
            if obj['name'] == 'Subject':
                email_details['subject'] = obj['value']
            if obj['name'] == 'Date':
                try:
                    date_value = obj['value']
                    date_value = datetime.strptime(
                        date_value, "%a, %d %b %Y %H:%M:%S %z")
                    date_value = date_value.strftime(
                        "%Y-%m-%d: %H:%M:%S")
                    email_details['received_on'] = date_value
                except Exception as e:
                    email_details['received_on'] = ''

        response = []
        attributes = ['sender', 'receiver', 'subject',
                      'snippet', 'received_on', 'read']
        for attr in attributes:
            response.append(email_details.get(attr, '1'))
        return tuple(response)

    def fetch_emails(self):
        creds = self.authenticate()
        service = build('gmail', 'v1', credentials=creds)

        results = service.users().messages().list(
            userId='me', labelIds=['INBOX'], maxResults=25).execute()
        messages = results.get('messages', [])
        if not messages:
            print('No emails found.')
            return None
        else:
            email_data = []
            for message in messages:
                msg = service.users().messages().get(
                    userId='me', id=message['id']).execute()
                email_data.append(self.format_email_data(msg))
        return email_data

    def insert_into_db(self):
        email_data = self.fetch_emails()
        try:
            # we will empty the table before inserting new data
            DB_Connections.empty_table('email.db', 'emails')
            DB_Connections.insert_into_table(email_data)
        except Exception as e:
            print('ERROR', e)
            print("ERROR WHILE INSERTING DATA INTO DB, RETRYING...")

        return None


class EmailOps:

    def join_any_rules(self, rules: list):
        new_rules = ''
        n = len(rules)
        for i, rule in enumerate(rules):
            if i == n-1:
                new_rules += rule
            else:
                new_rules += rule + 'OR'

        return new_rules

    def join_all_rules(self, rules: list):
        new_rules = ""
        n = len(rules)
        for i, rule in enumerate(rules):
            if i == n-1:
                new_rules += rule
            else:
                new_rules += rule + 'AND'
        return new_rules

    def perform_action(self, action, rules: list, all=False, any=False):
        if all:
            rules = self.join_all_rules(rules)
        elif any:
            rules = self.join_any_rules(rules)
        else:
            rules = rules[0]

        if action == 1:
            DB_Connections.delete_email(rules)
        elif action == 2:
            DB_Connections.read_or_unread(rules, True)
        elif action == 3:
            DB_Connections.select_from_table(rules)


if __name__ == '__main__':
    pass
    # # DB_Connections.create_table()
    # # email_fetcher = EmailFetcher()
    # # email_fetcher.insert_into_db()
    # # DB_Connections.select_from_table()
    # email_ops = EmailOps()
    # # print('OPS 1: We will mark read to all email having subject containing "Nikhil" or received after 2023-06-02')
    # # email_ops.perform_action(2, [RULES['2'], RULES['3']], any=True)

    # # print('OPS2: Retrieve all emails after a particular date')
    # # email_ops.perform_action(3, [RULES['3'], RULES['2']], all=True)

    # print('OPS3: we will delete the email sent from particular email address and have read')
    # email_ops.perform_action(1, [ RULES['1']])
