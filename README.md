# Graphene-Django-Extras

> [!WARNING]
> ## ⚠️ This project is deprecated and no longer maintained
>
> `graphene-django-extras` has been **rewritten from the ground up and renamed** to
> **[django-graphex](https://github.com/eamigo86/django-graphex)**.
>
> | | |
> |---|---|
> | **New repository** | https://github.com/eamigo86/django-graphex |
> | **New PyPI package** | https://pypi.org/project/django-graphex/ |
> | **Migration guide** | [docs/migration.md](https://github.com/eamigo86/django-graphex/blob/main/docs/migration.md) |
>
> Please migrate to `django-graphex`:
>
> ```bash
> uv add django-graphex          # or: pip install django-graphex
> ```
>
> This repository is kept **read-only, for historical reference**. No further
> releases, fixes or support will be provided here.

---

`graphene-django-extras` added pagination, filtering, DRF-serializer mutations and
directives on top of `graphene-django`. Its successor, **django-graphex**, keeps the
same ideas but is rebuilt on graphene + Pydantic (no DRF, no `graphene-django`
dependency), with automatic N+1 optimization, three pagination strategies, a
uniform nested-list shape, and an optional Channels-based subscriptions extra.

> **Subscriptions:** the standalone `graphene-django-subscriptions` package is also
> deprecated — subscriptions now ship inside `django-graphex` as the optional
> `[subscriptions]` extra.

## License

MIT — see [LICENSE](LICENSE).
