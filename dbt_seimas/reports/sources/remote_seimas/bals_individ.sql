SELECT
i.vardas ||' ' || i.pavarde AS seimo_narys,
COALESCE(i.kaip_balsavo, 'Nebalsavo') AS kaip_balsavo,
b.klausimu_grupes AS klausimu_grupes,
split_part(b.aprasas, '–', 2) AS balsuota_del,
b.balsavimo_laikas,
CASE i.kaip_balsavo WHEN 'Už' THEN 1 WHEN 'Susilaikė' THEN 0 WHEN 'Prieš' THEN -1 ELSE -2 END AS bals_int,
CASE
    WHEN b.aprasas LIKE '%Nepritarta%' THEN 'Nepritarta'
    WHEN b.aprasas LIKE '%Pritarta%' THEN 'Pritarta'
    ELSE 'Kita'
END AS rezultatas,
b.bals_id AS balsavimo_id
FROM seimas_dbt.balsavimai_individ i
LEFT JOIN seimas_dbt.balsavimai b
ON i.dlt_parent_id = b.dlt_id;