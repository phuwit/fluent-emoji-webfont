import shutil
from pathlib import Path

existing_path = Path("build")
fallback_paths: list[Path] = [Path('noto-emoji/third_party/region-flags/waved-svg'), Path('noto-emoji/svg')]

def main() -> None:
    for fallback_path in fallback_paths:
        existing_glyphs = set(i.name for i in existing_path.iterdir())
        fallback_candidate_glyphs = set(i.name for i in fallback_path.iterdir())

        fallback_glyphs = fallback_candidate_glyphs - existing_glyphs

        print(f'fallback on using {fallback_path} for {' '.join(fallback_glyphs)}')
        for glyph_name in fallback_glyphs:
            shutil.copy(fallback_path.joinpath(glyph_name), existing_path)

if (__name__ == '__main__'):
    main()
