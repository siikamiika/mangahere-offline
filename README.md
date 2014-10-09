# mangahere-offline

Yet another manga site ripper but also a reader that relies on a web browser instead of clunky comic readers.

## Install

Get python3 and install beautifulsoup4.

## How to download manga

`python3 mhdl.py type search here "with or without" quotes`
and select a result by entering a number

or

`python3 mhdl.py url http://www.mangahere.co/manga/some_manga/`


This will start downloading every chapter to the current directory. If chapter directories exist, they won't be redownloaded so be careful when interrupting downloads. Delete incomplete chapters before continuing download.

## How to read

### Locally

Open an index.html file inside any of the chapters. From there on, browser can be used to read other chapters.

### On a local network or a public network

Enable indexing on any web server or simply run `python3 -m http.server 8000`. Using a server has the advantage of not needing to click index.html every time when selecting a chapter from directory listing.

## updatereader_manual.py

It's actually an earlier implementation of creating index.html files in chapter directories but it can be used to update them if the file structure is modified afterwards.

### Usage

`python3 updatereader.py directory_name`
