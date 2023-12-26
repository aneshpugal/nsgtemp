import re

class BlobDetails:
    def __init__(self, blob_path):
        pattern = re.compile(r".*SUBSCRIPTIONS/(?P<subId>[^/]+)/RESOURCEGROUPS/(?P<resourceGroup>[^/]+)/PROVIDERS/MICROSOFT.NETWORK/NETWORKSECURITYGROUPS/(?P<nsgName>[^/]+)/y=(?P<blobYear>[^/]+)/m=(?P<blobMonth>[^/]+)/d=(?P<blobDay>[^/]+)/h=(?P<blobHour>[^/]+)/m=(?P<blobMinute>[^/]+)/macAddress=(?P<mac>[^/]+)/.*")
        match = pattern.match(blob_path)
        if match:
            self.subscription_id = match.group("subId")
            self.resource_group = match.group("resourceGroup")
            self.nsg_name = match.group("nsgName")
            self.year = match.group("blobYear")
            self.month = match.group("blobMonth")
            self.day = match.group("blobDay")
            self.hour = match.group("blobHour")
            self.minute = match.group("blobMinute")
            self.mac = match.group("mac")

    def get_partition_key(self):
        return f"{self.subscription_id.replace('-', '_')}_{self.resource_group}_{self.nsg_name}_{self.mac}"

    def get_row_key(self):
        return f"{self.year}_{self.month}_{self.day}_{self.hour}_{self.minute}"

    def __str__(self):
        return f"{self.resource_group}_{self.nsg_name}_{self.day}_{self.hour}"
