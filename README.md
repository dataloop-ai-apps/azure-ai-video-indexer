# Azure Video Indexer

Pipeline node for Audio features

1. Transcription (10 languages)
2. Speaker recognition

Pipeline node for Video features

1. Face detection (limited access?)
2. Object detection
3. Observed people
4. Content moderation (detect, no blurring)

## Deploy

To use the app you must have an integration secret with the following structure:

```json
{
    "AccountName": "<video indexer account name>",
    "ResourceGroup": "<video indexer account group>",
    "SubscriptionId": "",
    "accountId": "",
    "accountLocation": "",
    "ApiVersion": "2024-01-01",
    "ApiEndpoint": "https://api.videoindexer.ai",
    "AzureResourceManager": "https://management.azure.com",
    "tenantId": "",
    "applicationId": "",
    "applicationSecret": ""
}
```

You need to put those parameters in an organization integration in the following way

```python
import dtlpy as dl

project = dl.projects.get()
org: dl.Organization = project.org
with open('.env') as f:
    params = json.load(f)
    secrets = base64.b64encode(json.dumps(params).encode('ascii'))
org.integrations.create(integrations_type=dl.IntegrationType.KEY_VALUE,
                        name='azure_vi_integration',
                        options=secrets)
```