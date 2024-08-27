import requests
import config

from serializers.profile_serializer import serialize_profile_data


class DiscordServiceFetcher:
    def __init__(self, serviceTypeId="ALL"):
        self.serviceTypeId = serviceTypeId
        self.base_url=config.link_to_back
        self.total_elements = 0
        self.page_size = 0
        self.page_number = 0
        self.discordId = None
        self.services = []
        self.current_index = 0

    def fetch_services(self, page_size=20):
        if (self.serviceTypeId == "ALL"):
            url_to_send = self.base_url + f"?size={page_size}"
        else:
            print(f"?size={page_size}\n", f"serviceTypeId={self.serviceTypeId}")

            url_to_send = self.base_url + f"?size={page_size}" + f"&serviceTypeId={self.serviceTypeId}"
            print("url_for_back:", url_to_send)
        response = requests.get(url_to_send)
        if response.status_code == 200:
            data = response.json()
            self.total_elements = data['page']['totalElements']
            self.page_size = data['page']['size']
            self.page_number = data['page']['number']
            self.discordId = [service['discordId'] for service in data['_embedded']['discordServices']]
            serialized_services = [serialize_profile_data(service) for service in data['_embedded']['discordServices']]
            self.services = [
                {
                    "index": index,
                    "profile_id": "1446359f-dd6c-4c7f-9a46-1813736ebffd",
                    "discord_id": service['discord_id'],
                    "profile_username": service['profile_username'],
                    "service_title": service['service_title'],
                    "service_description": service['service_description'],
                    "service_price": service['service_price'],
                    "service_image": service['service_image'],
                    "service_type_id": service['service_type_id'],
                    "service_id": service['service_id']
                } for index, service in enumerate(serialized_services)
            ]
        else:
            response.raise_for_status()

    def get_services(self):
        return self.services

    def get_pagination_details(self):
        return {
            "totalElements": self.total_elements,
            "size": self.page_size,
            "page": self.page_number,
            "discord_id": self.discordId
        }

    def get_next(self):
        if self.current_index < len(self.services):
            service = self.services[self.current_index]
            self.current_index += 1
            return service
        else:
            if self.page_size < self.total_elements:
                self.page_size = self.total_elements
                self.fetch_services(page_size=self.page_size)
                return self.get_next()
            else:
                self.current_index = 0
                self.fetch_services(page_size=self.page_size)
                if self.total_elements == 0:
                    return False
                return self.get_next()

    def find(self, profileUsername):
        url_to_send = f"{self.base_url}/search/profileNameStartsWith?profileUsername={profileUsername}"
        response = requests.get(url_to_send)
        if response.status_code == 200:
            data = response.json()
            if '_embedded' in data and 'discordServices' in data['_embedded'] and data['_embedded']['discordServices']:
                service = serialize_profile_data(data['_embedded']['discordServices'][0])
                return {
                    "discord_id": service['discord_id'],
                    "profile_id": "1446359f-dd6c-4c7f-9a46-1813736ebffd",
                    "profile_username": service['profile_username'],
                    "service_title": service['service_title'],
                    "service_description": service['service_description'],
                    "service_price": service['service_price'],
                    "service_image": service['service_image'],
                    "service_type_id": service['service_type_id'],
                    "service_id": service['service_id']
                }
            else:
                return False
        else:
            response.raise_for_status()

    def find_by_id(self, discordId):
        url_to_send = f"{self.base_url}/search/profileNameStartsWith?discordId={discordId}"
        response = requests.get(url_to_send)
        if response.status_code == 200:
            data = response.json()
            if '_embedded' in data and 'discordServices' in data['_embedded'] and data['_embedded']['discordServices']:
                service = serialize_profile_data(data['_embedded']['discordServices'][0])
                return {
                    "discord_id": service['discord_id'],
                    "profile_id": "1446359f-dd6c-4c7f-9a46-1813736ebffd",
                    "profile_username": service['profile_username'],
                    "service_title": service['service_title'],
                    "service_description": service['service_description'],
                    "service_price": service['service_price'],
                    "service_image": service['service_image'],
                    "service_type_id": service['service_type_id'],
                    "service_id": service['service_id']
                }
            else:
                return False
        else:
            response.raise_for_status()

# print(DiscordServiceFetcher().find("hotanthinh113"))
