import dlt
from dlt.sources.helpers import requests
import xmltodict
import json

pipeline = dlt.pipeline(
    pipeline_name="kadencijos_pipeline",
    destination="clickhouse",
    dataset_name="seimo",
)

response = requests.get("http://apps.lrs.lt/sip/p2b.ad_seimo_kadencijos")
response.raise_for_status()
response = xmltodict.parse(response.content)
response = response["SeimoInformacija"]["SeimoKadencija"]
load_info = pipeline.run(response, table_name="kadencijos")

print(load_info)
