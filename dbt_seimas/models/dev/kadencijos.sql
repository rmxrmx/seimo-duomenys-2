select *
from {{ source('seimas', 'kadencijos') }}