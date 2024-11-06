---
title: Seimo Duomenys
---

```sql seimo_narys
 select id, vardas
 from remote_seimas.seimo_narys
 order by vardas desc
 ```

<Dropdown
  data={seimo_narys}
  name=seimo_nario_vardas
  value=vardas 
  title="Pasirinkite seimo narį" 
  defaultValue="Agnė Bilotaitė">
</Dropdown>

```sql kadencijos
select pavadinimas, data_nuo, data_iki
from remote_seimas.kadencijos
union
select 'Visos' as pavadinimas, make_date(1970, 01, 01) AS data_nuo, today() AS data_iki
```
<Dropdown
  data={kadencijos}
  name=kadencija
  value=pavadinimas
  title="Pasirinkite kadenciją"
  defaultValue="Visos">
</Dropdown>

```sql balsavimai
select *
from remote_seimas.bals_individ
where seimo_narys = '${inputs.seimo_nario_vardas.value}'
and balsavimo_laikas between
  (select data_nuo from ${kadencijos} where pavadinimas = '${inputs.kadencija.value}')
  and coalesce((select data_iki from ${kadencijos} where pavadinimas = '${inputs.kadencija.value}'), today())
order by balsavimo_laikas desc
```

<DataTable data={balsavimai} rows=15 search=true>
  <Column id=kaip_balsavo title="Balsas" contentType=colorscale scaleColumn=bals_int scaleColor={['#CA7373','#D7B26D','#3C552D']} colorMid=0/>
  <Column id=klausimu_grupes title="Klausimas" wrap=true/>
  <Column id=balsuota_del title="Aprašas" wrap=true/>
  <Column id=rezultatas title="Rezultatas"/>
  <Column id=balsavimo_laikas title="Data"/>
</DataTable>
<!-- balsavimai:
balsavimo pavadinimas, kaip balsavo, data, rezultatas, kaip balsavo frakcijos -->

```sql balsavimai_pie
select seimo_narys, COALESCE(kaip_balsavo, 'Nebalsavo') AS kaip_balsavo, count(*) / sum(count(*)) over() AS bals_pct
from remote_seimas.bals_individ
where seimo_narys = '${inputs.seimo_nario_vardas.value}'
and balsavimo_laikas between
  (select data_nuo from ${kadencijos} where pavadinimas = '${inputs.kadencija.value}')
  and coalesce((select data_iki from ${kadencijos} where pavadinimas = '${inputs.kadencija.value}'), today())
group by seimo_narys, kaip_balsavo
union
select 'Vidurkis' AS seimo_narys, COALESCE(kaip_balsavo, 'Nebalsavo'), count(*) / sum(count(*)) over() AS bals_pct
from remote_seimas.bals_individ
where balsavimo_laikas between
  (select data_nuo from ${kadencijos} where pavadinimas = '${inputs.kadencija.value}')
  and coalesce((select data_iki from ${kadencijos} where pavadinimas = '${inputs.kadencija.value}'), today())
group by kaip_balsavo
```

<BarChart 
    data={balsavimai_pie}
    x=seimo_narys
    y=bals_pct
    series=kaip_balsavo
    swapXY=false
    yFmt=pct
/>