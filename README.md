SharePointMaid
===

A repository to access files on SharePoint site using Graph API, SharePoint REST API v2, by Python.

![readme](https://user-images.githubusercontent.com/28250432/102326219-77730300-3fc7-11eb-8a42-8b0b5ae0822a.png)

## Ref urls

- [SharePoint APIs](https://docs.microsoft.com/ja-jp/sharepoint/dev/sp-add-ins/sharepoint-net-server-csom-jsom-and-rest-api-index)
- [Graph REST API v1.0](https://docs.microsoft.com/ja-jp/graph/api/overview?view=graph-rest-1.0) what this repository uses
- [Graph Explorer](https://developer.microsoft.com/ja-jp/graph/graph-explorer) what allows Graph API emurations

## Run on local env

Create .env

```
TENANT_ID=***
CLIENT_ID=***
CLIENT_SECRET=***
USER_OBJECT_ID=***
TARGET_SITE_ID=***
TARGET_FILE_PATH=***
```

## Set up Azure Active Directory application

- Make sure you have the Global administrator role.
- Go to Azure Active Directory.
- Left pane, App registrations > New registration
- Left pane, API permissions > Add permission
    - Select permission User > User.ReadWriteAll and Sites > Sites.ReadWriteAll
    - Push Grant admin consent for TENANT_NAME button
- Left pane, Certificates & secrets > + New client secret

Now you have...

- TENANT_ID
- CLIENT_ID
- CLIENT_SECRET

what you have to register as environment variables.
