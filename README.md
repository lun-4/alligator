# alligator

because i think [croc](croc)-but-its-tor-services would be a really, really funny idea

[croc]: https://github.com/schollz/croc

## how install

- get tor browser: https://torproject.org
  - keep it running while you run alli commands
- get python 3
- get python poetry: https://python-poetry.org/docs/#installation
  - make sure to switch `python` to `python3` on the pipe or else it will
    install itself as python2 which can lead to weirdness

```sh
git clone https://github.com/lun-4/alligator
poetry install
poetry run alli send myfile.txt
# copy the url provided and paste it after 'poetry run alli rx'
poetry run alli rx http://glaikjrgosihrgoislhr.onion/_alli/myfile.txt
```

## how it works

- `alli send` creates a tor hidden service whose only purpose is to send the file
- `alli receive` is a glorified downloader
- **TODO** once the download is finished, `alli send` destroys the hidden service
