"""
This Python script (re)generate topics
from Google Spreadsheets to MongoDB JSON collection
"""

import sys
import json
import itertools
from pathlib import Path

import pygsheets
import regex
from slugify import slugify

# Los recursos del paquete (credenciales y ficheros de referencia) se resuelven
# respecto a este fichero, para poder ejecutar el script desde cualquier directorio.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


class TopicsExtractor:

    def __init__(self, verbose=False, args=list()):
        self.GOOGLE_DRIVE_CREDENTIALS_FILE = BASE_DIR / "credentials.json"
        self.DATA_REFERENCE_FILE = args[1] if len(args) > 1 else ""
        self.verbose = verbose
        self.topics = list()
        self.data_reference = list()
        self.google_credentials = None

    def __regex_validation(self, tagname, regex_pattern):
        try:
            regex.compile("(?i)" + regex_pattern)
        except Exception as e:
            print(tagname, e)

    def __validate(self, tag):
        if tag["shuffle"]:
            delimiter = ".*?" if ".*?" in tag["regex"] else ".*"
            perms = itertools.permutations(tag["regex"].split(delimiter))
            for perm in perms:
                self.__regex_validation(tag["tag"], delimiter.join(perm))
        else:
            self.__regex_validation(tag["tag"], tag["regex"])

    def load_data_reference(self):
        if not self.DATA_REFERENCE_FILE:
            raise SystemExit(
                "Usage: python app.py <data_reference_name>.json\n"
                "Available: "
                + ", ".join(sorted(p.name for p in DATA_DIR.glob("*.json")))
            )
        data_reference_path = DATA_DIR / self.DATA_REFERENCE_FILE
        if not data_reference_path.is_file():
            raise SystemExit(
                "[ERROR] Data reference file not found: {}".format(data_reference_path)
            )
        with open(data_reference_path, "r") as data_reference_file:
            self.data_reference = json.load(data_reference_file)

    def load_google_credentials(self):
        self.google_credentials = pygsheets.authorize(
            service_account_file=str(self.GOOGLE_DRIVE_CREDENTIALS_FILE)
        )

    def load_topics(self):
        for data_reference_item in self.data_reference:
            if self.verbose:
                print("[EXTRACT] {}".format(data_reference_item["name"]))
            wks = self.google_credentials.open(data_reference_item["filename"]).sheet1
            topic = data_reference_item.copy()
            del topic["filename"]
            topic["_id"] = slugify(topic["shortname"].lower())
            topic["tags"] = []
            data = wks.get_values(
                grange=pygsheets.GridRange(worksheet=wks, start=None, end=None)
            )
            for row in data[1:]:
                if row[0] == "" or row[1] == "" or row[2] == "" or row[3] == "":
                    continue
                tag = {
                    "regex": row[3],
                    "tag": row[2],
                    "subtopic": row[1],
                    "shuffle": bool(int(row[0])),
                }
                self.__validate(tag)
                topic['knowledgebase'] = topic['knowledgebase']
                topic['public'] = True
                topic['tags'].append(tag)
            self.topics.append(topic)

    def export_topics(self):
        # La salida es un artefacto del usuario, asi que se escribe en el
        # directorio de trabajo actual, no dentro del paquete.
        output_path = Path("topics.json").resolve()
        with open(output_path, "w") as file_out:
            file_out.write(json.dumps(self.topics, indent=True, ensure_ascii=False))
        print("[EXPORT] Created {}".format(output_path))

    def run(self):
        self.load_data_reference()
        self.load_google_credentials()
        self.load_topics()
        self.export_topics()


if __name__ == "__main__":
    extractor = TopicsExtractor(verbose=True, args=sys.argv)
    extractor.run()
