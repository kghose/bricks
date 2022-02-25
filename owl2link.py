#!/usr/local/bin/python3

"""Convert a BrickOwl parts CSV to a BrickLink XML that can be imported into
BrickLink Studio

usage:

./owl2link.py brickowl_order_items.csv bricklink_studio.xml

"""

import argparse
from dataclasses import dataclass
import sys
from pathlib import Path
import csv


@dataclass
class Color:
    bo_str: str
    bo_id: int
    bl_str: str
    bl_id: int

    @classmethod
    def from_str(cls, bo: str, bl: str) -> "Color":
        bo_id, bo_str = cls._parse_str(bo)
        bl_id, bl_str = cls._parse_str(bl)
        return cls(bo_str, bo_id, bl_str, bl_id)

    @staticmethod
    def _parse_str(s: str):
        code, rest = s.split("['")
        code = int(code)
        return code, rest[:-2]

    def __str__(self) -> str:
        return f"{self.bo_str} -> {self.bl_id}"


@dataclass
class Part:
    part_no: str
    color: Color
    qty: int

    def as_brick_link(self, wishlist: bool = False, ignore_color: bool = False):
        return "".join(
            [
                "<ITEM><ITEMTYPE>P</ITEMTYPE>",
                f"<ITEMID>{self.part_no}</ITEMID>",
                ("" if ignore_color else f"<COLOR>{self.color.bl_id}</COLOR>"),
                (
                    f"<MINQTY>{self.qty}</MINQTY>"
                    if wishlist
                    else "<QTYFILLED>{self.qty}</QTYFILLED>"
                ),
                "</ITEM>\n",
            ]
        )

    def __eq__(self, __o: "Part") -> bool:
        return self.part_no == __o.part_no and self.color.bl_id == __o.color.bl_id

    def __hash__(self) -> int:
        return f"{self.part_no}_{self.color.bl_id}".__hash__()


class BrickOwl:
    def __init__(self) -> None:
        self._color_map = {}
        self._catalog = set()
        self._load_color_map()
        self._load_catalog()
        self._load_missing_parts()

    def part_from_row(self, name: str, color: str, quantity: str) -> Part:
        return Part(
            self._part_no_from_name(name),
            self._color_map.get(color.lower()),
            int(quantity),
        )

    def _load_color_map(self):
        with open("rebrickable-colormapping.csv") as color_csv:
            reader = csv.DictReader(color_csv)
            for row in reader:
                if row["BrickOwl"] and row["BrickLink"]:
                    col = Color.from_str(row["BrickOwl"], row["BrickLink"])
                    self._color_map[col.bo_str.lower()] = col

    def _load_catalog(self) -> set:
        with open("rebrickable-parts.csv") as catalog_csv:
            reader = csv.DictReader(catalog_csv)
            self._catalog = set(row["part_num"].strip() for row in reader)

    def _load_missing_parts(self) -> dict:
        with open("missing-parts.csv") as catalog_csv:
            reader = csv.DictReader(catalog_csv)
            self._missing_parts = {row["BO"]: row["BL"] for row in reader}

    def _part_no_from_name(self, name: str) -> int:
        """ "LEGO Dark Stone Gray Angle Connector #2 (180º) (32034 / 42134)" ->
        32034"""
        _part_no_fragment = name.rsplit("(", 1)[1][:-1]  # 32034 / 42134
        for _part_no in _part_no_fragment.split("/"):
            _part_no = _part_no.strip()
            if _part_no in self._missing_parts:
                return self._missing_parts.get(_part_no)
            if _part_no in self._catalog:
                return _part_no
        else:
            print(f"Could not find {name} (-> {_part_no}) in BrickLink catalog")
            return _part_no


def main(
    infile: Path, outfile: Path, wishlist: bool = False, ignore_color: bool = False
):
    bo = BrickOwl()

    parts = {}
    with open(infile) as brick_owl_csv:
        reader = csv.DictReader(brick_owl_csv)
        for row in reader:
            this_part = bo.part_from_row(
                name=row["Name"],
                color=row["Color Name"],
                quantity=int(row["Ordered Quantity"]),
            )
            if this_part not in parts:
                parts[this_part] = this_part
            else:
                parts[this_part].qty += this_part.qty

    with outfile.open("w") as studio_xml:
        studio_xml.write("<INVENTORY>\n")
        studio_xml.writelines(
            part.as_brick_link(wishlist, ignore_color) for part in parts.values()
        )
        studio_xml.write("</INVENTORY>\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BrickOwl CSV to BrickLink XML")
    parser.add_argument(
        "owl",
        type=str,
        help="BrickOwl CSV",
    )
    parser.add_argument(
        "link",
        type=str,
        help="BrickLink XML to write",
    )
    parser.add_argument(
        "--wishlist",
        action="store_true",
        help="Write as BL wishlist XML (rather than Stud.io part list)",
    )
    parser.add_argument(
        "--ignore-color",
        action="store_true",
        help="Ignore colors",
    )
    args = parser.parse_args()

    main(
        Path(args.owl),
        Path(args.link),
        wishlist=args.wishlist,
        ignore_color=args.ignore_color,
    )
