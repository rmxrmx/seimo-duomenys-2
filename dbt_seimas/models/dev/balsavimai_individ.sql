select *
from {{ source('seimas', 'balsavimai__individualiai') }}