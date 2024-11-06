
select
    posedzio_id,
    stadija,
    klausimu_grupes,
    abals_id AS bals_id,
    nuo,
    iki,
    aprasas,
    antraste,
    uzdaras,
    bendru_sutarimu,
    abalsavimo_laikas AS balsavimo_laikas,
    abalsavo AS balsavo,
    aviso AS viso,
    aux AS uz,
    apriex AS pries,
    asusilaikx AS susilaike,
    "_dlt_id" AS dlt_id

from {{ source('seimas', 'balsavimai') }}
