SELECT i.avardas ||' ' || i.apavardx AS seimo_narys, i.akaip_balsavo, b.klausimu_grupes, b.abalsavimo_laikas
FROM seimas_dbt.balsavimai_individ i
INNER JOIN seimas_dbt.balsavimai b
ON i."_dlt_parent_id" = b."_dlt_id"
WHERE b.bendru_sutarimu IS FALSE
ORDER BY b.abalsavimo_laikas DESC;