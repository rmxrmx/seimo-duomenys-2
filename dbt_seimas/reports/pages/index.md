---
title: Welcome to Evidence
---

<Details title='How to edit this page'>

  This page can be found in your project at `/pages/index.md`. Make a change to the markdown file and save it to see the change take effect in your browser.
</Details>

```sql seimo_narys
 select id, vardas
 from main_db.seimo_narys
 order by vardas desc
 ```

<Dropdown
  data={seimo_narys}
  name=seimo_narys
  value=vardas 
  title="Pasirinkite seimo narį" 
  defaultValue="Agnė Biliotaitė">
</Dropdown>

balsavimai:
balsavimo pavadinimas, kaip balsavo, data, rezultatas, kaip balsavo frakcijos
## What's Next?
- [Connect your data sources](settings)
- Edit/add markdown files in the `pages` folder
- Deploy your project with [Evidence Cloud](https://evidence.dev/cloud)

## Get Support
- Message us on [Slack](https://slack.evidence.dev/)
- Read the [Docs](https://docs.evidence.dev/)
- Open an issue on [Github](https://github.com/evidence-dev/evidence)
