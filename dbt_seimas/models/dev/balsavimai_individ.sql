select 
bi.aasmens_id AS asmens_id,
bi.avardas AS vardas,
bi.apavardx AS pavarde,
bi.afrakcija AS frakcija,
CASE bi.akaip_balsavo WHEN '' THEN NULL ELSE bi.akaip_balsavo END AS kaip_balsavo,
bi._dlt_parent_id AS dlt_parent_id,
bi._dlt_list_idx AS dlt_list_idx,
bi._dlt_id AS dlt_id,
b.abals_id AS balsavimo_id
from {{ source('seimas', 'balsavimai__individualiai') }} bi
LEFT JOIN {{ source('seimas', 'balsavimai')}} b
ON bi."_dlt_parent_id" = b."_dlt_id"
WHERE b.bendru_sutarimu IS FALSE