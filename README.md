# leandrobentancur.github.io

Source for Leandro Bentancur's academic site. One hand-edited data set in
`data/` renders every page, in English and Spanish, into `docs/`.

```sh
make all       # images, validation, site
make serve     # preview at localhost:8000
make status    # what is complete, what is pending
make reconcile # compare against the CVUy export from ANII
```

Requires `python3` with `pyyaml` and `jinja2`, plus ImageMagick for the images.

The LaTeX CVs are built from this same data, but not here: they come from a
sibling folder that is not published, since a CV is not part of the site.

**[ACTUALIZAR.md](ACTUALIZAR.md)** explains, in Spanish, how to update each
part — one recipe per situation. `CLAUDE.md` holds the same rules in the form
Claude needs them.
