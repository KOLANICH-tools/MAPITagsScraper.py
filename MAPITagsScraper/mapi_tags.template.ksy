meta:
  id: mapi_tags
  title: Outlook MAPI tags
  application:
    - Microsoft Outlook MAPI
    - Microsoft Exchange

doc: |
  Outlook MAPI tags are enums values used to identify various types of entities in various formats.

doc-ref:
  - https://docs.microsoft.com/en-us/openspecs/exchange_server_protocols/ms-oxprops/f6ab1613-aefe-447d-a49c-18217230b148
  - https://docs.microsoft.com/en-us/openspecs/exchange_server_protocols/ms-oxocntc/9b636532-9150-4836-9635-9c9b756c9ccf
  - https://github.com/hfig/MAPI/blob/master/src/MAPI/Schema/MapiFieldsMessage.yaml # MIT
  - https://github.com/hfig/MAPI/blob/master/src/MAPI/Schema/MapiFieldsOther.yaml # MIT
  - https://github.com/nektra/outlook-autocomplete/blob/master/OlAutoComplete/nk2props.h # MIT
  - https://github.com/stephenegriffin/mfcmapi/blob/151856e6ef5af42368a49a1340060aa58d981e8e/core/interpret/genTagArray.h # MIT
  - https://github.com/dbremner/pstviewtool/blob/52f59893ad4390358053541b0257b4a7f2767024/ptags.h  # Likely Apache. The repo contains no license, but the news (https://www.infoq.com/news/2010/05/Outlook-PST-View-Tool-and-SDK/, also https://web.archive.org/web/20140704101722/http://www.microsoft.com/en-us/news/press/2010/may10/05-24psttoolspr.aspx) claim that this tool and https://github.com/enrondata/pstsdk were published under Apache. Looks plausible since both software were authored by Terry Mahaffey (psviewtool has user name terrymah (though without a proper email) in git commits, likely the same guy as https://github.com/terrymah, pstsdk has the lines `\author Terry Mahaffey`)
