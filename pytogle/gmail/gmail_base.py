



class GmailBase:

    def _get_messages(self, next_page_token, label_ids, q):
        kwargs = {'userId': 'me', 'pageToken': next_page_token, 'q': q}
        if label_ids:
            kwargs['labelIds'] = label_ids
        data = self.service.message_service.list(**kwargs).execute()
        messages = iter(data.get("messages", []))
        next_page_token = data.get("nextPageToken", None)
        return messages, next_page_token


    def _get_message_raw_data(self, message_id):
        raw_message = self.service.message_service.get(userId = "me", id= message_id, format= "raw").execute()
        return raw_message


    def _get_history_data(self, start_history_id: int, history_types: list, label_id: str = None):
        perams = {
            'userId': 'me',
            'startHistoryId': start_history_id,
            'historyTypes': history_types
        }
        if label_id:
            perams['labelId'] = label_id
        data = self.service.history_service.list(**perams).execute()
        return data


    def _get_labels(self):
        data = self.service.labels_service.list(userId= 'me').execute()
        return data



    def _get_label_raw_data(self, label_id: str):
        data = self.service.labels_service.get(userId= 'me', id= label_id).execute()
        return data