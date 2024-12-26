#!/bin/bash

# Check arg
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <FONTTYPE>"
  echo "  FONTTYPE: color, flat or hc"
  exit 1
fi

if [ "$1" = 'color' ]; then
  FONTTYPE='Color'
elif [ "$1" = 'flat' ]; then
  FONTTYPE='Flat'
elif [ "$1" = 'hc' ]; then
  FONTTYPE='High Contrast'
fi

# On error, exit immediately.
set -e

# Remove potential leftovers from older builds.
rm -rf venv build

# Create clean Python environment.
python -m venv --upgrade-deps venv

# source venv/bin/activate
source venv/Scripts/activate # For Windows

pip install nanoemoji
pip install brotli # Add for conversion of woff2

# Prepare the emoji SVG files for nanoemoji by:
# 1) Renaming them from 'glyph_name.svg' to 'emoji_uxxxx.svg'.
# 2) Removing SVG masks them, as these are not compatible with picosvg.
#    When this happens, a message is printed, specifying the glyph. This
#    will slightly change how the glyph looks. This is preferred over not
#    including the glyph at all.
# 3) Moving them all into one common directory.
python -m prepare "${FONTTYPE}"

# Patch the nanoemoji package to exclude glyphs with incompatibilites
# instead of aborting completely.
# git apply --directory venv/lib/*/site-packages/nanoemoji nanoemoji.patch
git apply --directory venv/Lib/site-packages/nanoemoji nanoemoji.patch

# Build the ttf font file using the COLR1 format for the colored glyphs.
pushd build

CSSFILENAME=$(echo "FluentEmoji${FONTTYPE}.css" | sed 's/ //g')
echo -n >| "${CSSFILENAME}"

for i in {1..149} ; do
# for i in {1..3} ; do
  echo ${i}
  FILENUM=`printf "%03d" "${i}"`
  FILENAME=$(echo "FluentEmoji${FONTTYPE}${FILENUM}.ttf" | sed 's/ //g')
  echo "${FILENAME}"
  # echo $(find -maxdepth 1 -name '*.svg' | head -n $((20*i)) | tail -n 20)

  nanoemoji --color_format glyf_colr_1 --family "Fluent Emoji ${FONTTYPE}" --output_file "${FILENAME}" $(find -maxdepth 1 -name '*.svg' | head -n $((20*i)) | tail -n 20)
  
  pushd build
  maximum_color --bitmaps --output_file "${FILENAME}" "${FILENAME}"
  mv build/"${FILENAME}" ..
  popd
  
  # WOFFFILENAME=$(echo "FluentEmoji${FONTTYPE}${FILENUM}.woff" | sed 's/ //g')
  # fonttools ttLib ${FILENAME} --flavor woff -o ${WOFFFILENAME}
  WOFF2FILENAME=$(echo "FluentEmoji${FONTTYPE}${FILENUM}.woff2" | sed 's/ //g')
  fonttools ttLib "${FILENAME}" --flavor woff2 -o ../dist/"${WOFF2FILENAME}"

  UNICODERANGE=$( \
    echo $(find -maxdepth 1 -name '*.svg' | head -n $((20*i)) | tail -n 20) \
    | sed "s/.\/emoji_u/U+/g" \
    | sed "s/_/, U+/g" \
    | sed "s/.svg/,/g" \
    | sed "s/U+0*/U+/g" \
    | sed -z "s/,\n/;\n/g" \
  )

  echo "
  /* [${FILENUM}] */
  @font-face {
    font-family: 'Fluent Emoji ${FONTTYPE}';
    font-display: swap;
    src: url('/dist/${WOFF2FILENAME}') format('woff2');
    unicode-range: ${UNICODERANGE}
  }" >> "${CSSFILENAME}"
done

mv "${CSSFILENAME}" ../dist 

# Move the final font file to the build directory and clean up.
rm -rf build *.svg
popd
rm -rf venv
