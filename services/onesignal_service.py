from onesignal_sdk.client import Client
from core.settings import (
    ONESIGNAL_APP_ID,
    ONESIGNAL_REST_API_KEY
)


class OneSignalService:
    def __init__(self):
        self.client = Client(
            # api_key="wokad5e5zempuazyxoym34zea",
            app_id=ONESIGNAL_APP_ID,
            rest_api_key=ONESIGNAL_REST_API_KEY
        )

    def send_to_all(self,
                    heading="New Notification",
                    content="You have a new notification",
                    data=None):
        try:

            data = {'type': 'receipt'}
            notification_body = {
                'contents': {'en': content},
                'headings': {'en': heading},
                'data': data or {},
                'included_segments': ['All']
            }

            response = self.client.send_notification(notification_body)
            return response.body

        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            return None
