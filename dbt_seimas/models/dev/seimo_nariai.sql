SELECT aasmens_id AS id, avardas || ' ' || apavardx AS vardas, alytis AS lytis, MAX(abiografijos_nuoroda) AS nuoroda
FROM {{ source('seimas', 'seimo_nariai')}}
GROUP BY id, avardas, apavardx, alytis