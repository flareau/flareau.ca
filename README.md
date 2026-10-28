# flareau.ca

Site personnel statique construit avec [Hugo](https://gohugo.io/).

## Développement

```sh
make serve
```

Le site est alors disponible à l’adresse indiquée par Hugo. Pour produire la
version déployable dans `public/` :

```sh
make build
```

Tout le contenu à maintenir manuellement est regroupé dans `content/` :

- `content/pages/` contient les deux pages du site;
- `content/sections/` contient les sections Markdown du profil;
- `content/publications/publis.bib` contient la bibliographie;
- `content/publications/files/` contient les PDF.

Le `Makefile` régénère automatiquement `data/publications.json` avant chaque
prévisualisation ou build. Le reste du dépôt constitue la mécanique du site et
ne demande normalement aucune modification.

## TODO

- Bib2yaml: https://discourse.gohugo.io/t/bibtex-support/8879
