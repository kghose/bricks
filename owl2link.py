#!/usr/local/bin/python3

"""Interconvert parts lists to/from BrickOwl, Stud.io, BrickLink and ReBrickable
accepted formats."""

import argparse
import csv
from dataclasses import dataclass
import sys
from pathlib import Path
from typing import Dict, List


class PartsPath:
    def __init__(self, file_path: Path) -> None:
        self._path = file_path

    def as_bo(self) -> Path:
        return self._path.with_suffix(".csv")

    def as_std(self) -> Path:
        return self._path.with_suffix(".bricks")

    def as_bl(self) -> Path:
        return self._path.with_suffix(".xml")


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


class ColorConverter:
    def __init__(self) -> None:
        self._bo_name = {}
        self._bo_id = {}
        self._bl_id = {}
        with open("rebrickable-colormapping.csv") as color_csv:
            reader = csv.DictReader(color_csv)
            for row in reader:
                if row["BrickOwl"] and row["BrickLink"]:
                    col = Color.from_str(row["BrickOwl"], row["BrickLink"])
                    self._bo_name[col.bo_str.lower()] = col
                    self._bo_id[col.bo_id] = col
                    self._bl_id[col.bl_id] = col

    def from_bo_str(self, bo: str) -> Color:
        return self._bo_name[bo.lower()]

    def from_bo_id(self, bo_id: int) -> Color:
        return self._bo_id[bo_id]

    def from_bl_id(self, bl_id: int) -> Color:
        return self._bl_id[bl_id]


color_converter = ColorConverter()


@dataclass
class Part:
    part_no: str
    color: Color
    qty: int

    def as_brick_link(self, as_wishlist: bool = False, ignore_color: bool = False):
        return "".join(
            [
                "<ITEM><ITEMTYPE>P</ITEMTYPE>",
                f"<ITEMID>{self.part_no}</ITEMID>",
                ("" if ignore_color else f"<COLOR>{self.color.bl_id}</COLOR>"),
                (
                    f"<MINQTY>{self.qty}</MINQTY>"
                    if as_wishlist
                    else "<QTYFILLED>{self.qty}</QTYFILLED>"
                ),
                "</ITEM>\n",
            ]
        )

    def as_rebrickable(self):
        return f"{self.part_no},{self.color.bl_id},{self.qty}\n"

    def __eq__(self, __o: "Part") -> bool:
        return self.part_no == __o.part_no and self.color.bl_id == __o.color.bl_id

    def __hash__(self) -> int:
        return f"{self.part_no}_{self.color.bl_id}".__hash__()


class BrickOwl:
    def __init__(self) -> None:
        self._color_map = {}
        self._catalog = set()
        self._load_catalog()
        self._load_missing_parts()

    def part_from_row(self, name: str, color: str, quantity: str) -> Part:
        return Part(
            self._part_no_from_name(name),
            color_converter.from_bo_str(color),
            int(quantity),
        )

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


def load_bo(infile: Path) -> Dict[Part, Part]:
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
    return parts


def load_std(infile: Path) -> Dict[Part, Part]:
    parts = {}
    with open(infile) as std_csv:
        reader = csv.DictReader(std_csv)
        for row in reader:
            this_part = Part(
                part_no=row["part"],
                color=color_converter.from_bl_id(int(row["color"])),
                qty=int(row["quantity"]),
            )
            if this_part not in parts:
                parts[this_part] = this_part
            else:
                parts[this_part].qty += this_part.qty
    return parts


def to_studio(
    outfile: Path,
    parts: Dict[Part, Part],
    as_wishlist: bool = False,
    ignore_color: bool = False,
) -> None:
    with outfile.open("w") as studio_xml:
        studio_xml.write("<INVENTORY>\n")
        studio_xml.writelines(
            part.as_brick_link(as_wishlist, ignore_color) for part in parts.values()
        )
        studio_xml.write("</INVENTORY>\n")


def to_std(
    outfile: Path,
    parts: Dict[Part, Part],
) -> None:
    with outfile.open("w") as std_csv:
        std_csv.write("part,color,quantity\n")
        std_csv.writelines(part.as_rebrickable() for part in parts.values())


def owl2std(infile: Path) -> None:
    path = PartsPath(infile)
    parts = load_bo(path.as_bo())
    to_std(path.as_std(), parts)


def std2studio(
    infile: Path, as_wishlist: bool = False, ignore_color: bool = False
) -> None:
    path = PartsPath(infile)
    parts = load_std(path.as_std())
    to_studio(path.as_bl(), parts, as_wishlist=as_wishlist, ignore_color=ignore_color)


def main():
    parser = argparse.ArgumentParser(description="Parts Juggler")
    subparsers = parser.add_subparsers(title="Sub Commands")

    parser_from_bo = subparsers.add_parser(
        "from_owl", help="BrickOwl CSV to Standard CSV."
    )
    parser_from_bo.add_argument(
        "owl",
        type=str,
        help="BrickOwl CSV",
    )
    parser_from_bo.set_defaults(func=lambda args: owl2std(Path(args.owl)))

    parser_to_bl = subparsers.add_parser("to_bl", help="Standard CSV to BrickLink XML")
    parser_to_bl.add_argument(
        "std",
        type=str,
        help="Std CSV",
    )
    parser_to_bl.add_argument(
        "--as-wishlist",
        action="store_true",
        help="Write as BL wishlist XML (rather than Stud.io part list)",
    )
    parser_to_bl.add_argument(
        "--ignore-color",
        action="store_true",
        help="Ignore colors",
    )
    parser_to_bl.set_defaults(
        func=lambda args: std2studio(
            Path(args.std), as_wishlist=args.as_wishlist, ignore_color=args.ignore_color
        )
    )

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":

    main()
