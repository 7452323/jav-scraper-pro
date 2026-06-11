"""Fix NFO to match working format exactly."""
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

def _text(parent, tag, text):
    if text is not None:
        el = SubElement(parent, tag)
        el.text = str(text).strip()

root = Element("movie")
_text(root, "title", "FNS-151 新人太可爱了天夏由依 AVDEBUT")
_text(root, "sorttitle", "FNS-151")
_text(root, "originaltitle", "FNS-151")
se = SubElement(root, "set")
se.text = ""
_text(root, "rating", "0.0")
_text(root, "year", "2026")
_text(root, "mpaa", "XXX")
_text(root, "premiered", "2026-01-08")
_text(root, "release", "2026-01-08")
_text(root, "runtime", "120")
_text(root, "studio", "FALENO")
_text(root, "maker", "FALENO")
_text(root, "label", "FALENO")
_text(root, "plot", "FNS-151 新人太可爱了天夏由依 AVDEBUT")
_text(root, "outline", "FNS-151 新人太可爱了天夏由依 AVDEBUT")
_text(root, "genre", "JAV")
_text(root, "genre", "Censored")
ael = SubElement(root, "actor")
_text(ael, "name", "甘夏唯")
_text(ael, "role", "甘夏唯")
_text(ael, "thumb", "FNS-151-poster.jpg")
_text(root, "artist", "甘夏唯")
_text(root, "id", "FNS-151")
_text(root, "num", "FNS-151")
_text(root, "cover", "FNS-151-poster.jpg")
_text(root, "poster", "FNS-151-poster.jpg")
_text(root, "thumb", "FNS-151-thumb.jpg")
_text(root, "fanart", "FNS-151-fanart.jpg")

raw = tostring(root, encoding="unicode")
dom = xml.dom.minidom.parseString(raw)
xml_str = dom.toprettyxml(indent="  ")
xml_str = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n' + '\n'.join(xml_str.split('\n')[1:])

with open('output/FNS-151.nfo', 'w', encoding='utf-8') as f:
    f.write(xml_str)
print('Done')
