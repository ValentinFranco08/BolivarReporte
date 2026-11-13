"""Crea un tablero privado a partir del JSON de Bolívar Animal."""
import argparse
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def import_board(data, post, workspace=None):
    settings = dict(name=data["name"], desc=data["desc"], defaultLists="false",
                    defaultLabels="false", prefs_permissionLevel="private")
    if workspace:
        settings["idOrganization"] = workspace
    board = post("boards", **settings)
    print(f'Tablero creado: {board["url"]}', flush=True)
    lists = {item["id"]: post("lists", idBoard=board["id"], name=item["name"], pos="bottom")["id"]
             for item in data["lists"]}
    labels = {item["id"]: post("labels", idBoard=board["id"], name=item["name"], color=item["color"])["id"]
              for item in data["labels"]}
    cards = {}
    for item in data["cards"]:
        fields = dict(idList=lists[item["idList"]], name=item["name"], desc=item["desc"], pos="bottom")
        if item["idLabels"]:
            fields["idLabels"] = ",".join(labels[label] for label in item["idLabels"])
        cards[item["id"]] = post("cards", **fields)["id"]
    for item in data["checklists"]:
        checklist = post("checklists", idCard=cards[item["idCard"]], name=item["name"], pos="bottom")
        for check in item["checkItems"]:
            post(f'checklists/{checklist["id"]}/checkItems', name=check["name"], pos="bottom",
                 checked=str(check["state"] == "complete").lower())
    return board["url"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path)
    parser.add_argument("--workspace", help="ID del Workspace de destino, si corresponde")
    parser.add_argument("--apply", action="store_true", help="Crear el tablero en Trello")
    args = parser.parse_args()
    data = json.loads(args.json_file.read_text(encoding="utf-8"))
    criteria = sum(len(check["checkItems"]) for check in data["checklists"])
    print(f'{len(data["lists"])} listas, {len(data["cards"])} tarjetas y {criteria} criterios.')
    if not args.apply:
        return
    key, token = os.getenv("TRELLO_KEY"), os.getenv("TRELLO_TOKEN")
    if not key or not token:
        parser.error("Definí TRELLO_KEY y TRELLO_TOKEN antes de usar --apply.")

    def post(path, **fields):
        request = Request(f"https://api.trello.com/1/{path}", data=urlencode(fields).encode(),
                          headers={"Authorization": f'OAuth oauth_consumer_key="{key}", oauth_token="{token}"',
                                   "Accept": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except (HTTPError, URLError) as error:
            status = error.code if isinstance(error, HTTPError) else type(error.reason).__name__
            raise SystemExit(f"Error en POST /{path} ({status}). Si ya se creó el tablero, quedó parcial.") from None

    print(f"Importación completa: {import_board(data, post, args.workspace)}")


if __name__ == "__main__":
    main()
