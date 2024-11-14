# {params.seimo_narys}

```sql kadencijos
select pavadinimas, data_nuo, data_iki
from remote_seimas.kadencijos
where exists (
  select balsavimo_laikas
  from remote_seimas.bals_individ
  where seimo_narys = '${params.seimo_narys}'
  and balsavimo_laikas between data_nuo::date and coalesce(data_iki::date, today()+1)
)
union
select 'Visos' as pavadinimas, make_date(1970, 01, 01) AS data_nuo, today()+1 AS data_iki
```

{#if kadencijos.length > 0}
  <Dropdown
    data={kadencijos}
    name=kadencija
    value=pavadinimas
    title="Pasirinkite kadenciją"
    defaultValue="Visos">
  </Dropdown>

  ```sql balsavimai
  select
    kaip_balsavo,
    klausimu_grupes,
    balsuota_del,
    rezultatas,
    balsavimo_laikas,
    bals_int,
    '/balsavimai/' || balsavimo_id as balsavimo_link 
  from remote_seimas.bals_individ
  where seimo_narys = '${params.seimo_narys}'
  and balsavimo_laikas between
    (select data_nuo from ${kadencijos} where pavadinimas = '${inputs.kadencija.value}')
    and coalesce((select data_iki from ${kadencijos} where pavadinimas = '${inputs.kadencija.value}'), today()+1)
  order by balsavimo_laikas desc
  ```

  <DataTable data={balsavimai} rows=15 search=true>
    <Column id=kaip_balsavo title="Balsas" contentType=colorscale scaleColumn=bals_int scaleColor={['#CA7373','#D7B26D','#3C552D']} colorMid=0/>
    <Column id=klausimu_grupes title="Klausimas" wrap=true/>
    <Column id=balsuota_del title="Aprašas" wrap=true/>
    <Column id=balsavimo_link contentType=link linkLabel=rezultatas title="Rezultatas"/>
    <Column id=balsavimo_laikas title="Data"/>
  </DataTable>
  <!-- balsavimai:
  balsavimo pavadinimas, kaip balsavo, data, rezultatas, kaip balsavo frakcijos -->

  ```sql balsavimai_pie
  select seimo_narys, COALESCE(kaip_balsavo, 'Nebalsavo') AS kaip_balsavo, count(*) / sum(count(*)) over() AS bals_pct
  from remote_seimas.bals_individ
  where seimo_narys = '${params.seimo_narys}'
  and balsavimo_laikas between
    (select data_nuo from ${kadencijos} where pavadinimas = '${inputs.kadencija.value}')
    and coalesce((select data_iki from ${kadencijos} where pavadinimas = '${inputs.kadencija.value}'), today()+1)
  group by seimo_narys, kaip_balsavo
  union
  select 'Vidurkis' AS seimo_narys, COALESCE(kaip_balsavo, 'Nebalsavo'), count(*) / sum(count(*)) over() AS bals_pct
  from remote_seimas.bals_individ
  where balsavimo_laikas between
    (select data_nuo from ${kadencijos} where pavadinimas = '${inputs.kadencija.value}')
    and coalesce((select data_iki from ${kadencijos} where pavadinimas = '${inputs.kadencija.value}'), today()+1)
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

{:else}
  Šis seimo narys neturi balsavimų, vykusių po 1999 metų, kai šie duomenys buvo pradėti skaitmenizuoti.

{/if}