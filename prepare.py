import sys
from functools import partial
from json import loads
from operator import ne
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import parse, register_namespace, tostring
import subprocess

def main():
    args = sys.argv
    fonttype = args[1]
    dest_dir = Path("build")
    glyph_map: dict[Path, Path] = {}
    numElementsGroupCriteria = 20
    fallback_paths: list[Path] = [Path('noto-emoji/third_party/region-flags/waved-svg'), Path('noto-emoji/svg')]


    def getCodePoint(glyph_dir: str):
        glyph_metadata_path = glyph_dir / "metadata.json"
        glyph_metadata: dict[str, Any] = loads(
            glyph_metadata_path.read_text(encoding="utf-8")
        )

        # Get the codepoint(s) for the emoji.
        codepoint: str = glyph_metadata["unicode"]
        codepoint = "_".join(filter(partial(ne, "fe0f"), codepoint.split(" ")))
        return codepoint


    def isCodepointWorkAroundTarget(codePointText: str):
        targetList = [
            "🏃",
            "🏄",
            "🏊",
            "🏋",
            "🏌",
            "👮",
            "👰",
            "👱",
            "👳",
            "👷",
            "💁",
            "💂",
            "💆",
            "💇",
            "🕵",
            "🙅",
            "🙆",
            "🙇",
            "🙋",
            "🙍",
            "🙎",
            "🚣",
            "🚴",
            "🚵",
            "🚶",
            "🤦",
            "🤵",
            "🤷",
            "🤸",
            "🤹",
            "🤽",
            "🤾",
            "🦸",
            "🦹",
            "🧍",
            "🧎",
            "🧏",
            "🧖",
            "🧗",
            "🧘",
            "🧙",
            "🧚",
            "🧛",
            "🧜",
            "🧝",
            "🧞",
            "🧟",
            "🫃",
            "⛹",
        ]

        # to prevent each font file from getting too big.
        removeTargetList = [
            "🏃🏿‍➡️",
            "🏄🏿‍♂️",
            "🏊🏿‍♂️",
            "🏋🏿‍♂️",
            "🏌🏿‍♂️",
            "👮🏿‍♂️",
            "👰🏿‍♂️",
            "👱🏿‍♂️",
            "👳🏿‍♂️",
            "👷🏿‍♂️",
            "💁🏿‍♂️",
            "💂🏿‍♂️",
            "💆🏿‍♂️",
            "💇🏿‍♂️",
            "🕵🏿‍♂️",
            "🙅🏿‍♂️",
            "🙆🏿‍♂️",
            "🙇🏿‍♂️",
            "🙋🏿‍♂️",
            "🙍🏿‍♂️",
            "🙎🏿‍♂️",
            "🚣🏿‍♂️",
            "🚴🏿‍♂️",
            "🚵🏿‍♂️",
            "🚶🏿‍➡️",
            "🤦🏿‍♂️",
            "🤵🏿‍♂️",
            "🤷🏿‍♂️",
            "🤸🏿‍♂️",
            "🤹🏿‍♂️",
            "🤽🏿‍♂️",
            "🤾🏿‍♂️",
            "🦸🏿‍♂️",
            "🦹🏿‍♂️",
            "🧍🏿‍♂️",
            "🧎🏿‍➡️",
            "🧏🏿‍♂️",
            "🧖🏿‍♂️",
            "🧗🏿‍♂️",
            "🧘🏿‍♂️",
            "🧙🏿‍♂️",
            "🧚🏿‍♂️",
            "🧛🏿‍♂️",
            "🧜🏿‍♂️",
            "🧝🏿‍♂️",
            "🧞‍♂️",
            "🧟‍♂️",
            "🫄🏿",
            "⛹🏿‍♂️",
        ]

        for removeTarget in removeTargetList:
            removeTargetCodePointText = ""
            for removeTargetCP in removeTarget:
                removeTargetCodePointText += format(ord(removeTargetCP), "x") + "_"
            removeTargetCodePointText = removeTargetCodePointText[: -len("_")]
            removeTargetCodePointText = removeTargetCodePointText.replace("_fe0f", "")
            # print(removeTargetCodePointText)
            if codePointText == removeTargetCodePointText:
                return False

        for target in targetList:
            targetCodePoint = format(ord(target), "x")
            if targetCodePoint in codePointText:
                return True

        return False


    def makeGlyphMap(glyph_dir: str):
        numGroup = 0
        numElementsGroup = 0
        glyph_metadata_path = glyph_dir / "metadata.json"
        glyph_metadata: dict[str, Any] = loads(
            glyph_metadata_path.read_text(encoding="utf-8")
        )

        # Get the codepoint(s) for the emoji.
        if "unicodeSkintones" not in glyph_metadata:
            # Emoji with no skin tone variations.
            codepoint: str = glyph_metadata["unicode"]
            codepoint = "_".join(filter(partial(ne, "fe0f"), codepoint.split(" ")))
            gCodePoint = codepoint
            # print(f"{fonttype}/*.svg")
            src_path = next(glyph_dir.glob(f"{fonttype}/*.svg"))
            glyph_map[src_path] = (
                dest_dir / f"{numGroup:03}_{numElementsGroup:03}_emoji_u{codepoint}.svg"
            )
            numElementsGroup += 1
        else:
            # Emoji with skin tone variations.
            var_metadata: list[str] = glyph_metadata["unicodeSkintones"]
            for codepoint in var_metadata:
                codepoint = "_".join(filter(partial(ne, "fe0f"), codepoint.split(" ")))
                skintone = (
                    skintone_map.get(codepoint.split("_")[1], "Default")
                    if "_" in codepoint
                    else "Default"
                )
                if fonttype == "High Contrast":
                    src_path = next(glyph_dir.glob(f"Default/{fonttype}/*.svg"))
                    src_path = Path(f"HC{skintone}" + str(src_path))
                else:
                    src_path = next(glyph_dir.glob(f"{skintone}/{fonttype}/*.svg"))
                glyph_map[src_path] = (
                    dest_dir / f"{numGroup:03}_{numElementsGroup:03}_emoji_u{codepoint}.svg"
                )
                gCodePoint = codepoint
                numElementsGroup += 1
        if numElementsGroup > numElementsGroupCriteria:
            # continue as workaround
            if isCodepointWorkAroundTarget(gCodePoint):
                print(f"continue as workaround, {numGroup}, {numElementsGroup}")
            else:
                numGroup += 1
                numElementsGroup = 0

    def prepare_fallback(fallback_path: Path):
        existing_glyphs = set(i.name() for i in dest_dir.iterdir())
        fallback_candidate_glyphs = set(i.name() for i in fallback_path.iterdir())

        fallback_glyphs = fallback_candidate_glyphs - existing_glyphs

        for glyph_name in fallback_glyphs:
            subprocess.run(f'cp {fallback_path.joinpath(glyph_name)} {dest_dir}', check=True)



    skintone_map = {
        "1f3fb": "Light",
        "1f3fc": "Medium-Light",
        "1f3fd": "Medium",
        "1f3fe": "Medium-Dark",
        "1f3ff": "Dark",
    }

    # Patch to fix the issue #23
    subprocess.run(
        "sed -i -e 's/1f3c3 1f3c3 200d 27a1 fe0f/1f3c3 1f3fc 200d 27a1 fe0f/' './fluentui-emoji/assets/Person running facing right/metadata.json'",
        shell=True,
        check=True
    )

    # Replace target SVGs
    replaceTargetSVGList = list(Path("replaceSVG").iterdir())
    for svgFile in replaceTargetSVGList:
        print(f"find ./fluentui-emoji/ -name {svgFile.name}")
        subprocess.run(
            f"find ./fluentui-emoji/ -name {svgFile.name} | xargs -I {{}} cp {str(svgFile)} {{}}",
            shell=True,
            check=True
        )

    pathList = list(Path("fluentui-emoji/assets").iterdir())
    sortedPathList = sorted(pathList, key=getCodePoint)
    prioritizedGlyphs = [
        "💻",
        "🔥",
        "🔬",
        "🗨️",
        "🚀",
        "🚒",
        "🟩",
        "🟫",
        "🦺",
        "🦼",
        "🦽",
        "↔️",
        "↕️",
        "☠️",
        "♀️",
        "♂️",
        "⚕️",
        "⚖️",
        "⚧️",
        "✈️",
        "❄️",
        "➡️",
        "⬛",
        "💼",
        "🔧",
        "🦯",
    ]
    prioritizedGlyphDirPathList = []

    for glyph_dir in sortedPathList:
        glyph_metadata_path = glyph_dir / "metadata.json"
        glyph_metadata: dict[str, Any] = loads(
            glyph_metadata_path.read_text(encoding="utf-8")
        )

        prioritizedGlyphFound = False
        for prioritizedGlyph in prioritizedGlyphs:
            if glyph_metadata["glyph"] == prioritizedGlyph:
                prioritizedGlyphDirPathList.append(glyph_dir)
                prioritizedGlyphFound = True

        if prioritizedGlyphFound == True:
            continue

        makeGlyphMap(glyph_dir)

    for glyph_dir in prioritizedGlyphDirPathList:
        makeGlyphMap(glyph_dir)

    # Remove incompatible <mask> elements from SVG files.
    dest_dir.mkdir()
    register_namespace("", "http://www.w3.org/2000/svg")
    for src_path, dest_path in glyph_map.items():
        if fonttype == "High Contrast":
            for skintone in [
                "Default",
                "Light",
                "Medium-Light",
                "Medium",
                "Medium-Dark",
                "Dark",
            ]:
                src_path_str = str(src_path)
                if skintone in src_path_str:
                    src_path = src_path_str.replace(
                        f"HC{skintone}fluentui-emoji", "fluentui-emoji"
                    )
        tree = parse(src_path)
        for elem in tree.iter():
            for mask in elem.findall("{http://www.w3.org/2000/svg}mask"):
                elem.remove(mask)
                print(
                    f"Removed incompatible mask from {src_path.stem} ({dest_path.stem})."
                    " Resulting SVG may look different."
                )
        dest_path.write_text(tostring(tree.getroot(), encoding="unicode"))


    for fallpack_path in fallback_paths:
        prepare_fallback(fallback_path=fallpack_path)

if (__name__ == '__main__'):
    main()