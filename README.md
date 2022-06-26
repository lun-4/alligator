# alligator

because i think [croc](croc)-but-its-tor-services would be a really, really funny idea

[croc]: https://github.com/schollz/croc

## how install

```
git clone ...
poetry install
poetry run alli
```

## how it works

- `alli send` creates a tor hidden service whose only purpose is to send the file
- `alli receive` is a glorified downloader
- once the download is finished, `alli send` destroys the hidden service
