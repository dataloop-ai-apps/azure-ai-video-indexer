import os
import json
import base64
import dtlpy as dl

from VideoIndexerClient.Consts import Consts
from VideoIndexerClient.VideoIndexerClient import VideoIndexerClient

from modules import AudioIndexer, VideoIndexer


class Adapter(dl.BaseServiceRunner):
    def __init__(self, azure_vi_integration=''):
        secrets = os.environ.get(azure_vi_integration, None)
        if secrets is None:
            if not os.path.isfile('.env'):
                raise ValueError('Missing integration id. Cannot load video indexer')
            with open('.env') as f:
                params = json.load(f)
        else:
            params = json.loads(base64.b64decode(eval(secrets)))

        for k, v in params.items():
            os.environ[k] = v

        # create and validate consts
        consts = Consts(ApiVersion=os.environ['ApiVersion'],
                        ApiEndpoint=os.environ['ApiEndpoint'],
                        AzureResourceManager=os.environ['AzureResourceManager'],
                        AccountName=os.environ['AccountName'],
                        ResourceGroup=os.environ['ResourceGroup'],
                        SubscriptionId=os.environ['SubscriptionId'])
        account = {"location": os.environ['accountLocation'],
                   "properties": {"accountId": os.environ['accountId']}}
        # create Video Indexer Client
        client = VideoIndexerClient(consts=consts, account=account)
        client.get_vi_access_token(tenant_id=os.environ['tenantId'],
                                   application_id=os.environ['applicationId'],
                                   application_secret=os.environ['applicationSecret'])
        self.client = client

    def run_video(self, item: dl.Item):
        if "azureIndexerVideoId" in item.system:
            video_id = item.system['azureIndexerVideoId']
        else:
            filepath = item.download(overwrite=True)
            video_id = self.client.file_upload_async(media_path=filepath,
                                                     video_name=item.id,
                                                     excluded_ai=[])
            item.metadata['system']['azureIndexerVideoId'] = video_id
            item.update(True)
            os.remove(filepath)

        results = self.client.wait_for_index_async(video_id)
        with open(f'results_{item.id}.json', 'w') as f:
            json.dump(results, f, indent=2)
        extractor = VideoIndexer()
        extractor.extract(item=item, results=results)

    def run_audio(self, item: dl.Item):
        if "azureIndexerVideoId" in item.system:
            video_id = item.system['azureIndexerVideoId']
        else:
            filepath = item.download(overwrite=True)
            video_id = self.client.file_upload_async(media_path=filepath,
                                                     video_name=item.id,
                                                     excluded_ai=[])
            item.metadata['system']['azureIndexerVideoId'] = video_id
            item.update(True)
            os.remove(filepath)

        if os.path.isfile(f'results_{item.id}.json'):
            with open(f'results_{item.id}.json') as f:
                results = json.load(f)
        else:
            results = self.client.wait_for_index_async(video_id)
            with open(f'results_{item.id}.json', 'w') as f:
                json.dump(results, f, indent=2)
        extractor = AudioIndexer()
        extractor.extract(item=item, results=results)


if __name__ == "__main__":
    self = Adapter()
