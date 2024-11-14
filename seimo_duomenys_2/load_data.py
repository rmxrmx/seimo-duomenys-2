import os
from xml.parsers.expat import ExpatError
import dlt
from dlt.sources.helpers import requests
import xmltodict
import duckdb
from dotenv import load_dotenv

headers = {
    "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"
}


@dlt.resource(name="kadencijos", write_disposition="replace")
def kadencijos():
    kadencijos_xml = requests.get(
        "http://apps.lrs.lt/sip/p2b.ad_seimo_kadencijos", headers=headers
    )
    kadenciju_data = xmltodict.parse(kadencijos_xml.content)["SeimoInformacija"][
        "SeimoKadencija"
    ]
    for kadencija in kadenciju_data:
        yield kadencija


@dlt.resource(name="sesijos", write_disposition="replace")
def sesijos():
    sesijos_xml = requests.get(
        "http://apps.lrs.lt/sip/p2b.ad_seimo_sesijos?ar_visos=T", headers=headers
    )
    sesijos_su_kadencijomis = xmltodict.parse(sesijos_xml.content)["SeimoInformacija"][
        "SeimoKadencija"
    ]
    for kadencija in sesijos_su_kadencijomis:
        if "SeimoSesija" in kadencija:
            if isinstance(kadencija["SeimoSesija"], list):
                for sesija in kadencija["SeimoSesija"]:
                    yield {"kadencijos_id": kadencija["@kadencijos_id"]} | sesija
            else:
                yield {"kadencijos_id": kadencija["@kadencijos_id"]} | kadencija[
                    "SeimoSesija"
                ]


@dlt.resource(name="seimo_nariai", primary_key="aasmens_id", write_disposition="merge")
def seimo_nariai():
    for kadencija in kadencijos():
        kadencijos_id = kadencija["@kadencijos_id"]
        nariai_xml = requests.get(
            "http://apps.lrs.lt/sip/p2b.ad_seimo_nariai?kadencijos_id="
            + str(kadencijos_id),
            headers=headers,
        )
        try:
            nariai = xmltodict.parse(nariai_xml.content)["SeimoInformacija"][
                "SeimoKadencija"
            ]["SeimoNarys"]
            for narys in nariai:
                yield {"kadencijos_id": kadencijos_id} | narys
        except ExpatError:
            print(f"seimo_nariai extract failed with kadencija {kadencijos_id}")


# TODO: limit by time
@dlt.resource(name="posedziai", write_disposition="replace")
def posedziai():
    for sesija in sesijos():
        sesijos_id = sesija["@sesijos_id"]
        posedziu_xml = requests.get(
            "http://apps.lrs.lt/sip/p2b.ad_seimo_posedziai?sesijos_id="
            + str(sesijos_id),
            headers=headers,
        )
        posedziu_data = xmltodict.parse(posedziu_xml.content)["SeimoInformacija"][
            "SeimoSesija"
        ]
        if "SeimoPosėdis" not in posedziu_data:
            continue
        posedziu_data = posedziu_data["SeimoPosėdis"]

        if isinstance(posedziu_data, dict):
            posedziu_data = [posedziu_data]
        for posedis in posedziu_data:
            yield {"sesijos_id": sesijos_id} | posedis


def klausimu_grupes(klausimas: dict) -> str:
    if "klausimų grupė" in klausimas["pavadinimas"].lower():
        return klausimas["pavadinimas"] + " " + klausimas["nr"]
    else:
        return klausimas["pavadinimas"]


# TODO: limit by time
@dlt.resource(name="balsavimai", write_disposition="append")
def balsavimai(data_nuo: str):
    for posedis in posedziai():
        posedzio_id = posedis["@posėdžio_id"]
        posedzio_pradzia = posedis["@pradžia"]
        if data_nuo >= posedzio_pradzia:
            continue
        posedzio_eiga_xml = requests.get(
            "http://apps.lrs.lt/sip/p2b.ad_seimo_posedzio_eiga_full?posedzio_id="
            + posedzio_id,
            headers=headers,
        )
        posedzio_eiga = xmltodict.parse(posedzio_eiga_xml.content)["posedziai"][
            "posedis"
        ]["posedzio-eiga"]
        if posedzio_eiga:
            posedzio_eiga = posedzio_eiga["darbotvarkes-klausimas"]
        else:
            continue
        if isinstance(posedzio_eiga, dict):
            posedzio_eiga = [posedzio_eiga]
        for klausimas in posedzio_eiga:
            if "balsavimai" in klausimas and klausimas["balsavimai"]:
                if isinstance(klausimas["balsavimai"], dict):
                    klausimas["balsavimai"] = [klausimas["balsavimai"]]
                for balsavimai in klausimas["balsavimai"]:
                    balsavimai = balsavimai["balsavimas"]
                    if isinstance(balsavimai, dict):
                        balsavimai = [balsavimai]
                    for balsavimas in balsavimai:
                        balsavimas_extra = vienas_balsavimas(balsavimas["@bals_id"])
                        balsavimas["uzdaras"] = False

                        if "pritarta bendru sutarimu" in balsavimas["antraste"].lower():
                            balsavimas["bendru_sutarimu"] = True
                        else:
                            balsavimas["bendru_sutarimu"] = False
                            if balsavimas_extra["@balsavo"] == 0:
                                balsavimas["uzdaras"] = True

                        yield {
                            "posedzio_id": posedzio_id,
                            "stadija": (
                                klausimas["stadija"] if "stadija" in klausimas else None
                            ),
                            "klausimu_grupes": klausimu_grupes(klausimas),
                        } | balsavimas | balsavimas_extra


def vienas_balsavimas(balsavimo_id: str) -> dict:
    balsavimas_xml = requests.get(
        "http://apps.lrs.lt/sip/p2b.ad_sp_balsavimo_rezultatai?balsavimo_id="
        + balsavimo_id,
        headers=headers,
    )
    balsavimas = xmltodict.parse(balsavimas_xml.content)["SeimoInformacija"][
        "SeimoNariųBalsavimas"
    ]
    return balsavimas["BendriBalsavimoRezultatai"] | {
        "individualiai": balsavimas["IndividualusBalsavimoRezultatas"]
    }


@dlt.source
def seimas_source(start_step: int, end_step: int = 10, balsai_nuo: str = "1970-01-01"):
    resources = [kadencijos, sesijos, seimo_nariai, posedziai, balsavimai(balsai_nuo)]
    return resources[start_step:end_step]


if __name__ == "__main__":
    load_dotenv()
    pipeline = dlt.pipeline(
        pipeline_name="seimo_duomenys",
        destination="motherduck",
        dataset_name="seimas_raw",
        progress="tqdm",
    )

    con = duckdb.connect(
        f"md:remote_seimas?motherduck_token={os.getenv("MOTHERDUCK_API")}"
    )
    data_nuo = con.sql("SELECT MAX(aprad_ia) FROM seimas_raw.posedziai;").fetchone()[0]
    con.close()
    load_info = pipeline.run(seimas_source(0, 5, str(data_nuo)))
    print(load_info)

    pipeline = dlt.pipeline(
        pipeline_name="seimo_duomenys",
        destination="motherduck",
        dataset_name="seimas_dbt",
        progress="tqdm",
    )

    # Get runner
    dbt = dlt.dbt.package(
        pipeline,
        "./dbt_seimas/",
    )

    # Run the models and collect any info
    # If running fails, the error will be raised with a full stack trace
    models = dbt.run_all()

    # On success, print the outcome
    for m in list(models):
        print(
            f"Model {m.model_name} materialized"
            + f" in {round(m.time,2)}s"
            + f" with status {m.status}"
            + f" and message {m.message}"
        )
