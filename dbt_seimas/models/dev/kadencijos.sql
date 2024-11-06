select
    akadencijos_id AS kadencijos_id,
    apavadinimas AS pavadinimas,
    adata_nuo::date AS data_nuo,
    CASE WHEN adata_iki = '' THEN NULL ELSE adata_iki::date END AS data_iki

from {{ source('seimas', 'kadencijos') }}