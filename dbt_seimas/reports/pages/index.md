---
title: Seimo Duomenys
---

```sql seimo_narys
 select
  id,
  vardas AS seimo_narys,
  '/seimo-nariai/' || vardas AS seimo_narys_link
 from remote_seimas.seimo_narys
 order by vardas asc
 ```
<DataTable
  data={seimo_narys}
  link=seimo_narys_link
  search=true
/>

```sql balsavimai
select '/balsavimai/' || bals_id AS bals_link
from remote_seimas.balsavimai
```