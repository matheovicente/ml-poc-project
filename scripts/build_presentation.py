from __future__ import annotations

import html
import shutil
import zipfile
from pathlib import Path


PROJECT_DIR = Path("/Users/matheovicente/Documents/Codex/DÉTROIT MARITIMES")
PLOTS_DIR = PROJECT_DIR / "plots"
OUTPUT_DIR = PROJECT_DIR / "deliverables"
OUTPUT_PPTX = OUTPUT_DIR / "maritime_straits_10min_presentation.pptx"

SLIDE_W = 13_333_333
SLIDE_H = 7_500_000


def emu(inches: float) -> int:
    return int(inches * 914400)


def text_box(
    shape_id: int,
    x: float,
    y: float,
    w: float,
    h: float,
    lines: list[str],
    font_size: int = 22,
    bold: bool = False,
    color: str = "1F2937",
) -> str:
    paragraphs = []
    for line in lines:
        paragraphs.append(
            f"""
            <a:p>
              <a:r>
                <a:rPr lang="fr-FR" sz="{font_size * 100}" b="{1 if bold else 0}">
                  <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
                </a:rPr>
                <a:t>{html.escape(line)}</a:t>
              </a:r>
              <a:endParaRPr lang="fr-FR" sz="{font_size * 100}"/>
            </a:p>
            """
        )
    return f"""
    <p:sp>
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="TextBox {shape_id}"/>
        <p:cNvSpPr txBox="1"/>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:noFill/>
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" anchor="t"/>
        <a:lstStyle/>
        {''.join(paragraphs)}
      </p:txBody>
    </p:sp>
    """


def title_box(title: str, subtitle: str | None = None) -> str:
    parts = [
        text_box(2, 0.55, 0.35, 12.2, 0.6, [title], font_size=30, bold=True, color="0F172A")
    ]
    if subtitle:
        parts.append(text_box(3, 0.58, 0.95, 11.8, 0.35, [subtitle], font_size=14, color="64748B"))
    return "".join(parts)


def bullet_box(shape_id: int, x: float, y: float, w: float, h: float, bullets: list[str]) -> str:
    return text_box(shape_id, x, y, w, h, [f"• {bullet}" for bullet in bullets], font_size=18)


def image_box(shape_id: int, rel_id: str, x: float, y: float, w: float, h: float) -> str:
    return f"""
    <p:pic>
      <p:nvPicPr>
        <p:cNvPr id="{shape_id}" name="Image {shape_id}"/>
        <p:cNvPicPr/>
        <p:nvPr/>
      </p:nvPicPr>
      <p:blipFill>
        <a:blip r:embed="{rel_id}"/>
        <a:stretch><a:fillRect/></a:stretch>
      </p:blipFill>
      <p:spPr>
        <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
      </p:spPr>
    </p:pic>
    """


def rectangle(shape_id: int, x: float, y: float, w: float, h: float, color: str) -> str:
    return f"""
    <p:sp>
      <p:nvSpPr><p:cNvPr id="{shape_id}" name="Rectangle {shape_id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
        <a:ln><a:noFill/></a:ln>
      </p:spPr>
    </p:sp>
    """


def slide_xml(content: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {content}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def slide_rels(image_targets: list[str]) -> str:
    rels = [
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
    ]
    for idx, target in enumerate(image_targets, start=2):
        rels.append(
            f'<Relationship Id="rId{idx}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{target}"/>'
        )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{''.join(rels)}</Relationships>"""


def build_slides() -> list[dict]:
    img = {
        "malacca": PLOTS_DIR / "closure_simulations" / "malacca_strait_90d_n_total_focus.png",
        "hormuz": PLOTS_DIR / "closure_simulations" / "strait_of_hormuz_90d_n_total_focus.png",
        "taiwan": PLOTS_DIR / "closure_simulations" / "taiwan_strait_90d_n_total_focus.png",
        "backtest": PLOTS_DIR / "backtests" / "malacca_strait_90d_backtest.png",
    }
    slides = []

    slides.append(
        {
            "content": slide_xml(
                rectangle(20, 0, 0, 13.33, 7.5, "F8FAFC")
                + text_box(2, 0.75, 1.25, 11.6, 0.9, ["Fermeture des détroits maritimes"], 36, True, "0F172A")
                + text_box(3, 0.78, 2.08, 11.2, 0.9, ["Simulation d'impact sur les grands chokepoints mondiaux"], 24, False, "334155")
                + text_box(4, 0.78, 3.25, 10.8, 1.6, [
                    "Objectif : identifier les détroits les plus critiques et estimer comment une fermeture de 14, 30 ou 90 jours peut déplacer le trafic maritime."
                ], 21, False, "1F2937")
                + text_box(5, 0.78, 6.45, 8, 0.3, ["Projet ML - PortWatch AIS - Présentation 10 minutes"], 13, False, "64748B")
            ),
            "images": [],
        }
    )

    slides.append(
        {
            "content": slide_xml(
                title_box("Problématique concrète", "Une fermeture ne touche pas seulement le détroit fermé : elle peut saturer ou déplacer le trafic ailleurs.")
                + bullet_box(4, 0.75, 1.75, 11.8, 2.3, [
                    "Quels détroits sont les plus critiques dans le réseau maritime mondial ?",
                    "Si l'un des grands détroits ferme, quels autres détroits changent réellement ?",
                    "Sur 2 semaines, 1 mois et 3 mois, observe-t-on un choc ponctuel ou une nouvelle trajectoire ?",
                ])
                + text_box(5, 0.8, 4.75, 11.4, 1.2, [
                    "Question finale : peut-on construire un outil de simulation simple, lisible et défendable pour comparer l'impact de plusieurs scénarios de fermeture ?"
                ], 23, True, "0F172A")
            ),
            "images": [],
        }
    )

    slides.append(
        {
            "content": slide_xml(
                title_box("Données utilisées", "Dataset PortWatch : observations journalières de trafic maritime par chokepoint.")
                + bullet_box(4, 0.75, 1.65, 6.2, 3.2, [
                    "74 844 lignes observées",
                    "28 chokepoints maritimes",
                    "Variables : trafic total, tankers, cargos, passagers, date et localisation",
                    "Détroit d'Ormuz inclus dans le dataset",
                ])
                + text_box(5, 7.2, 1.75, 5.4, 3.6, [
                    "Pourquoi ce dataset est pertinent ?",
                    "",
                    "Il permet d'étudier un impact maritime réel, sans passer par les marchés financiers.",
                    "",
                    "La donnée AIS donne une mesure opérationnelle : nombre de navires observés par jour."
                ], 19, False, "1F2937")
            ),
            "images": [],
        }
    )

    slides.append(
        {
            "content": slide_xml(
                title_box("Pipeline du projet", "Du dataset brut vers un outil de scoring, de prévision et de simulation.")
                + text_box(4, 0.9, 1.65, 11.6, 3.7, [
                    "1. Nettoyage et agrégation des séries journalières",
                    "2. Construction d'indicateurs : volume moyen, part de tankers, volatilité, dépendance au trafic",
                    "3. Score de criticité pour classer les détroits",
                    "4. Modèles ML pour reproduire les classes de criticité",
                    "5. SARIMAX pour prévoir le trafic normal",
                    "6. Simulation de fermeture : trafic fermé à zéro + redistribution partielle vers alternatives plausibles",
                ], 19, False, "1F2937")
                + text_box(5, 0.9, 6.05, 11.2, 0.5, [
                    "Le projet ne prédit pas chaque navire individuellement : il estime des effets agrégés, plus robustes pour une présentation."
                ], 16, True, "334155")
            ),
            "images": [],
        }
    )

    slides.append(
        {
            "content": slide_xml(
                title_box("Quels détroits ressortent ?", "Classement par score de criticité construit à partir du volume et du rôle stratégique.")
                + text_box(4, 0.9, 1.55, 11.6, 4.6, [
                    "1. Malacca Strait : score 81.5 | 196.9 navires/jour | 75.3 tankers/jour",
                    "2. Taiwan Strait : score 65.5 | 241.4 navires/jour | 55.4 tankers/jour",
                    "3. Strait of Hormuz : score 58.4 | 87.1 navires/jour | 52.2 tankers/jour",
                    "4. Bohai Strait : score 58.1 | 175.0 navires/jour | 36.4 tankers/jour",
                    "5. Korea Strait : score 56.0 | 223.2 navires/jour | 61.7 tankers/jour",
                    "",
                    "Lecture : Ormuz n'est pas le premier en volume total, mais il ressort très haut grâce au poids des tankers."
                ], 18, False, "1F2937")
            ),
            "images": [],
        }
    )

    slides.append(
        {
            "content": slide_xml(
                title_box("Fiabilité temporelle", "SARIMAX sert à prévoir le trafic normal avant d'appliquer un choc de fermeture.")
                + image_box(4, "rId2", 0.7, 1.45, 7.1, 4.6)
                + text_box(5, 8.05, 1.55, 4.7, 4.35, [
                    "Résultat de backtest :",
                    "",
                    "SARIMAX réduit l'erreur MAE d'environ 27 % en moyenne par rapport à la baseline analog.",
                    "",
                    "Sur 90 jours, Malacca passe de 21.7 à 15.5 navires/jour d'erreur moyenne.",
                    "",
                    "Conclusion : le modèle capte mieux le niveau normal et la saisonnalité hebdomadaire."
                ], 17, False, "1F2937")
            ),
            "images": [img["backtest"]],
        }
    )

    slides.append(
        {
            "content": slide_xml(
                title_box("Scénario 1 : fermeture de Malacca", "Un choc sur Malacca touche un détroit à très fort volume et très forte intensité tanker.")
                + image_box(4, "rId2", 0.55, 1.25, 8.0, 5.45)
                + text_box(5, 8.8, 1.65, 4.0, 4.7, [
                    "Lecture du graphique :",
                    "",
                    "La ligne verticale marque le début de fermeture.",
                    "",
                    "Le trafic du détroit fermé tombe à zéro.",
                    "",
                    "Les autres courbes montrent les détroits réellement impactés dans la simulation focus."
                ], 17, False, "1F2937")
            ),
            "images": [img["malacca"]],
        }
    )

    slides.append(
        {
            "content": slide_xml(
                title_box("Scénario 2 : fermeture d'Ormuz", "Ormuz est moins volumineux que Malacca, mais beaucoup plus sensible pour l'énergie.")
                + image_box(4, "rId2", 0.55, 1.25, 8.0, 5.45)
                + text_box(5, 8.8, 1.55, 4.0, 4.9, [
                    "Point clé :",
                    "",
                    "La redistribution est volontairement limitée, car les alternatives maritimes crédibles à Ormuz sont faibles.",
                    "",
                    "C'est donc un scénario plus géopolitique que simplement logistique.",
                    "",
                    "À présenter comme un stress test, pas comme une prédiction parfaite."
                ], 17, False, "1F2937")
            ),
            "images": [img["hormuz"]],
        }
    )

    slides.append(
        {
            "content": slide_xml(
                title_box("Scénario 3 : fermeture de Taiwan", "Un détroit très fréquenté, au centre d'un espace régional déjà dense.")
                + image_box(4, "rId2", 0.55, 1.25, 8.0, 5.45)
                + text_box(5, 8.8, 1.55, 4.0, 4.9, [
                    "Ce cas est utile pour les slides :",
                    "",
                    "Il montre mieux les effets locaux en Asie de l'Est.",
                    "",
                    "Les changements visibles concernent surtout les détroits proches ou connectés.",
                    "",
                    "Cela rend le projet concret : on observe où le choc se propage."
                ], 17, False, "1F2937")
            ),
            "images": [img["taiwan"]],
        }
    )

    slides.append(
        {
            "content": slide_xml(
                title_box("Conclusion", "Le projet produit un outil concret de comparaison des fermetures de détroits.")
                + bullet_box(4, 0.8, 1.55, 11.6, 3.3, [
                    "Les détroits les plus critiques ne sont pas seulement les plus fréquentés : le type de trafic compte.",
                    "SARIMAX améliore la prévision du trafic normal et donne une baseline défendable.",
                    "Les fermetures simulées montrent surtout des effets régionaux, avec peu d'alternatives crédibles pour Ormuz.",
                    "Le livrable est tangible : classements, métriques, graphiques de scénario et application Streamlit.",
                ])
                + text_box(5, 0.85, 5.65, 11.2, 0.85, [
                    "Limite principale : les règles de redistribution sont une modélisation métier simplifiée. La prochaine étape serait d'intégrer les distances, routes AIS réelles et temps de détour."
                ], 18, True, "0F172A")
            ),
            "images": [],
        }
    )

    return slides


def content_types(n_slides: int, media_count: int) -> str:
    slide_overrides = "".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, n_slides + 1)
    )
    media_overrides = "".join(
        f'<Override PartName="/ppt/media/image{i}.png" ContentType="image/png"/>'
        for i in range(1, media_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  {media_overrides}
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  {slide_overrides}
</Types>"""


def presentation_xml(n_slides: int) -> str:
    slide_ids = "".join(f'<p:sldId id="{255+i}" r:id="rId{i}"/>' for i in range(1, n_slides + 1))
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId{n_slides + 1}"/></p:sldMasterIdLst>
  <p:sldIdLst>{slide_ids}</p:sldIdLst>
  <p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""


def presentation_rels(n_slides: int) -> str:
    rels = [
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, n_slides + 1)
    ]
    rels.append(
        f'<Relationship Id="rId{n_slides + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    )
    rels.append(
        f'<Relationship Id="rId{n_slides + 2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>'
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{''.join(rels)}</Relationships>"""


ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


APP_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
  <PresentationFormat>On-screen Show (16:9)</PresentationFormat>
</Properties>"""


CORE_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:dcmitype="http://purl.org/dc/dcmitype/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Fermeture des détroits maritimes</dc:title>
  <dc:creator>Matheo Vicente</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
</cp:coreProperties>"""


THEME_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Simple">
  <a:themeElements>
    <a:clrScheme name="Simple">
      <a:dk1><a:srgbClr val="0F172A"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="1F2937"/></a:dk2><a:lt2><a:srgbClr val="F8FAFC"/></a:lt2>
      <a:accent1><a:srgbClr val="2563EB"/></a:accent1><a:accent2><a:srgbClr val="0F766E"/></a:accent2>
      <a:accent3><a:srgbClr val="DC2626"/></a:accent3><a:accent4><a:srgbClr val="F59E0B"/></a:accent4>
      <a:accent5><a:srgbClr val="7C3AED"/></a:accent5><a:accent6><a:srgbClr val="475569"/></a:accent6>
      <a:hlink><a:srgbClr val="2563EB"/></a:hlink><a:folHlink><a:srgbClr val="7C3AED"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Simple">
      <a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont>
      <a:minorFont><a:latin typeface="Aptos"/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Simple">
      <a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
      <a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
      <a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
      <a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
</a:theme>"""


SLIDE_LAYOUT_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""


SLIDE_LAYOUT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""


SLIDE_MASTER_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
</p:sldMaster>"""


SLIDE_MASTER_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""


def build_pptx() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slides = build_slides()

    media_files: list[Path] = []
    slide_media_names: list[list[str]] = []
    media_index = 1
    for slide in slides:
        names = []
        for image_path in slide["images"]:
            if not image_path.exists():
                raise FileNotFoundError(image_path)
            media_name = f"image{media_index}.png"
            media_files.append(image_path)
            names.append(media_name)
            media_index += 1
        slide_media_names.append(names)

    if OUTPUT_PPTX.exists():
        OUTPUT_PPTX.unlink()

    with zipfile.ZipFile(OUTPUT_PPTX, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types(len(slides), len(media_files)))
        zf.writestr("_rels/.rels", ROOT_RELS)
        zf.writestr("docProps/app.xml", APP_XML)
        zf.writestr("docProps/core.xml", CORE_XML)
        zf.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        zf.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(len(slides)))
        zf.writestr("ppt/theme/theme1.xml", THEME_XML)
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", SLIDE_LAYOUT_XML)
        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", SLIDE_LAYOUT_RELS)
        zf.writestr("ppt/slideMasters/slideMaster1.xml", SLIDE_MASTER_XML)
        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", SLIDE_MASTER_RELS)

        for i, slide in enumerate(slides, start=1):
            zf.writestr(f"ppt/slides/slide{i}.xml", slide["content"])
            zf.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", slide_rels(slide_media_names[i - 1]))

        for i, media_file in enumerate(media_files, start=1):
            zf.writestr(f"ppt/media/image{i}.png", media_file.read_bytes())

    copy_path = OUTPUT_DIR / "maritime_straits_10min_presentation_copy.pptx"
    shutil.copyfile(OUTPUT_PPTX, copy_path)
    print(OUTPUT_PPTX)


if __name__ == "__main__":
    build_pptx()
