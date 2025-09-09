# Changelog

All notable changes to `graphene-django-extras` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-09-08

### Changed
- Updated CI/CD configuration to use tox.ini
- Improved GitHub Actions workflows
- Relaxed django-filter constraint for Django 5 compatibility

### Fixed
- Fixed CI/CD pipeline configuration issues
- Made DjangoListField.type compatible with graphene-django 3

## [1.0.0] - 2023-01-23

### Added
- Major stable release
- Official Python 3.10 support
- Support for Django 3.2, 4.0, 4.1, and 4.2
- Support for Django 5.0 and 5.1 (added in later patches)
- Pre-commit hooks configuration
- Comprehensive documentation with MkDocs
- Support to Django 4.x

### Changed
- **Breaking**: Dropped Python 3.6, 3.7, 3.8, and 3.9 support (now requires Python 3.10+)
- Updated django-filter dependency to 22.1+
- Replaced deprecated `force_text` with `force_str` for Django 4+ compatibility
- Updated Django REST Framework and pytest dependencies
- Modernized development toolchain with black, isort, flake8, mypy
- Enhanced testing with pytest and coverage

### Fixed
- Fixed TypeError in directives import
- Fixed compatibility issues with graphene-django 3
- Always add registry to `_meta` for new filterset compatibility
- Fixed issues with Django 4+ compatibility

### Removed
- Dropped support for end-of-life Python versions (3.6-3.9)
- Dropped support for Django versions < 3.2
- Removed deprecated whitelist usage in tox configuration

## [0.5.2] - 2021-07-01

### Added
- Custom resolver logic for DjangoFilterPaginateListField
- Treat DjangoFilterPaginateListField the same as DjangoListField for NONNULL handling

### Changed
- Enhanced GitHub Actions CI/CD pipeline
- Updated dependencies and documentation
- Improved custom resolver support

### Fixed
- Fixed custom user resolver logic to use custom resolvers instead of default manager queryset

## [0.5.1] - 2021-07-01

### Changed
- Update dependencies

## [0.5.0] - 2021-03-22

### Added
- Enhanced documentation system
- Improved dependency management
- Updated development workflow with GitHub Actions
- Upgrade to graphene v3

### Changed
- Updated project dependencies
- Improved documentation structure and content
- Enhanced development and testing workflows

## [0.4.9] - Previous Release

### Changed
- Upgrade graphene-django dependency to version == 2.6.0

## [0.4.8] - Previous Release

### Changed
- Upgrade graphene-django dependency to version == 2.6.0

## [0.4.6] - Previous Release

### Added
- The tests were refactored and added some extra tests for DjangoSerializerType

### Changed
- Upgrade graphql-core dependency to version >= 2.2.1
- Upgrade graphene dependency to version >= 2.1.8
- Upgrade graphene-django dependency to version >= 2.5.0
- Upgrade django-filter dependency to version >= 2.2.0

### Fixed
- Fixed bug 'DjangoSerializerOptions' object has no attribute 'interfaces' after update to graphene==2.1.8

## [0.4.5] - 2021-06-30

### Added
- Support for Django 3.2 LTS
- Enhanced filtering capabilities
- Improved mutation field customization

### Changed
- Better handling of large datasets in pagination
- Enhanced directive performance
- Improved error reporting in mutations
- Fixed compatibilities issues to use graphene-django>=2.3.2
- Improved code quality and use Black code format

### Fixed
- Fixed issue with multiple pagination classes
- Resolved filtering edge cases with null values
- Fixed directive argument validation
- Fixed minor bug with "time ago" date directive

## [0.4.3] - Previous Release

See git history for detailed changes in versions 0.4.3 and earlier.

## [0.4.0] - 2021-08-20

### Added
- Major release with breaking changes
- New DjangoSerializerMutation class
- Comprehensive directive system
- Advanced pagination features
- Enhanced filtering capabilities

### Changed
- Complete rewrite of mutation system
- Better integration with Django REST Framework
- Enhanced GraphQL schema generation
- Improved error handling

### Breaking Changes
- Old mutation classes deprecated
- Changed pagination API
- Updated directive syntax
- Modified filtering interface

## Legacy Versions (0.3.x and below)

### [0.3.7]
- Improved DjangoListType and DjangoObjectType to share the filterset_class between the two class

### [0.3.6]
- Improve DjangoSerializerMutation resolvers

### [0.3.5]
- Fixed minor bug on ExtraGraphQLDirectiveMiddleware
- Fixed error with DRF 3.8 Compatibility
- Updated List's Fields to pass info.context to filterset as request, this allow filtering by request data
- Added new feature to ordering paginated queries

### [0.3.4-alpha2]
- Fixed minor bug on DjangoListObjectType

### [0.3.4-alpha1]
- Added filterset_class to the listing types as default filter
- Changed getOne by RetrieveField on DjangoListObjectType

### [0.3.3]
- Added filterset_class to DjangoObjectType
- Fixed minor bug on factory_types function

### [0.3.3-alpha1]
- Fixed minor bug on queryset_factory function

### [0.3.2]
- Updated Date directive format function for better string format combinations
- Updated custom Time, Date and DateTime base types to be used with Date directive
- Fixed bug with caching Introspection queries on ExtraGraphQLView

### [0.3.1]
- Fixed bug with default Date directive format

### [0.3.0]
- Added Binary graphql type. A BinaryArray is used to convert a Django BinaryField to the string form
- Added 'CACHE_ACTIVE' and 'CACHE_TIMEOUT' config options to GRAPHENE_DJANGO_EXTRAS settings for activate cache queries result and define a expire time. Default values are: CACHE_ACTIVE=False, CACHE_TIMEOUT=300 (5 minutes)
- Updated Date directive for use with Django TimeField, DateField, and DateTimeField
- Updated ExtraGraphQLView and AuthenticatedGraphQLView to allow use subscription requests on graphene-django >=2.0
- Updated setup dependence to graphene-django>=2.0

### [0.2.2]
- Fixed performance bug on some queries when request nested ManyToMany fields

### [0.2.1]
- Fixed bug with default PaginationClass and DjangoFilterPaginateListField

### [0.2.0]
- Added some useful directives to use on queries and fragments
- Fixed error on DjangoFilterPaginateListField resolve function

### [0.1.6]
- Fixed bug on create and update function on serializer mutation

### [0.1.3]
- Fixed some minors bugs

### [0.1.2]
- Added ok field and errors field to DjangoSerializerType like on DjangoSerializerMutation
- Added possibility of filtering in those queries fields that return a list of objects
- Updated DRF compatibility
- Fixed bug with filters when use global DEFAULT_PAGINATION_CLASS

### [0.1.1]
- Fixed error with JSONField reference on Django==1.8.x installations

### [0.1.0]
- Added DjangoSerializerType for quick Django's models types definition
- Moved support for Subscriptions to graphene-django-subscriptions packages for incompatibility with graphene-django>=2.0
- Fixed bug on DjangoFilterPaginateListField's pagination

### [0.1.0-alpha12]
- Added new settings param: MAX_PAGE_SIZE, to use on GRAPHENE_DJANGO_EXTRAS configuration dict for better customize DjangoListObjectType's pagination
- Added support to Django's field: GenericRel
- Improve model's fields calculation for to add all possible related and reverse fields
- Improved documentation translation

### [0.1.0-alpha11]
- Improved ordering for showed fields on graphqli's IDE
- Added better descriptions for auto generated fields

### [0.1.0-alpha10]
- Improve converter.py file to avoid create field for auto generate OneToOneField product of an inheritance
- Fixed bug in Emun generation for fields with choices of model inheritance child

### [0.1.0-alpha9]
- Fixed bug on GenericType and GenericInputType generations for Queries list Type and Mutations

### [0.1.0-alpha6]
- Fixed with exclude fields and converter function

### [0.1.0-alpha5]
- Updated to graphene-django>=2.0
- Fixed minor bugs on queryset_builder performance

### [0.1.0-alpha4]
- Add queryset options to DjangoListObjectType Meta class for specify wanted model queryset
- Add AuthenticatedGraphQLView on graphene_django_extras.views for use 'permission', 'authorization' and 'throttle' classes based on the DRF settings

### [0.1.0-alpha3]
- Fixed bug on subscriptions when not specified any field in "data" parameter to bean return on notification message

### [0.1.0-alpha2]
- Fixed bug when subscribing to a given action (create, update or delete)
- Added intuitive and simple web tool to test notifications of graphene-django-extras subscription

### [0.1.0-alpha1]
- Added support to multiselect choices values for models.CharField with choices attribute, on queries and mutations
- Added support to GenericForeignKey and GenericRelation fields, on queries and mutations
- Added first approach to support Subscriptions with Channels, with subscribe and unsubscribe operations
- Fixed minors bugs

### [0.0.4]
- Fix error on DateType encode

### [0.0.3]
- Implement custom implementation of DateType for use converter and avoid error on Serializer Mutation

### [0.0.2]
- Changed dependency of DRF to 3.6.4 on setup.py file, to avoid an import error produced by some changes in new version of DRF=3.7.0 and because DRF 3.7.0 dropped support to Django versions < 1.10

### [0.0.1]
- Fixed bug on DjangoInputObjectType class that refer to unused interface attribute
- Added support to create nested objects like in DRF, it's valid to SerializerMutation and DjangoInputObjectType, only is necessary to specify nested_fields=True on its Meta class definition
- Added support to show, only in mutations types to create objects and with debug=True on settings, inputs autocomplete ordered by required fields first
- Fixed others minors bugs

### [0.0.1-rc.2]
- Make queries pagination configuration is more friendly

### [0.0.1-rc.1]
- Fixed a bug with input fields in the converter function

### [0.0.1-beta.10]
- Fixed bug in the queryset_factory function because it did not always return a queryset

### [0.0.1-beta.9]
- Remove hard dependence with psycopg2 module
- Fixed bug that prevented use queries with fragments
- Fixed bug relating to custom django_filters module and ordering fields

### [0.0.1-beta.6]
- Optimizing imports, fix some minors bugs and working on performance

### [0.0.1-beta.5]
- Repair conflict on converter.py, by the use of get_related_model function with: OneToOneRel, ManyToManyRel and ManyToOneRel

### [0.0.1-beta.4]
- First commit

## Contributing

We welcome contributions! Please see our [contributing guidelines](contributing.md) for details on how to:

- Report bugs
- Suggest features  
- Submit pull requests
- Improve documentation

## Support

### Compatibility Matrix

| graphene-django-extras | Python | Django | Graphene | graphene-django |
|----------------------|--------|---------|-----------|----------------|
| 1.0.1 | 3.10-3.12 | 3.2-5.1 | 3.0+ | 3.2+ |
| 1.0.0 | 3.10-3.12 | 3.2-5.0 | 3.0+ | 3.2+ |
| 0.5.2 | 3.7-3.10 | 3.2-4.2 | 3.0+ | 3.0+ |
| 0.5.0 | 3.7-3.10 | 3.2-4.1 | 3.0+ | 3.0+ |
| 0.4.5 | 3.7-3.10 | 3.2-4.1 | 3.0-3.1 | 3.0+ |

### Getting Help

- 📚 [Documentation](https://github.com/eamigo86/graphene-django-extras)
- 🐛 [Issue Tracker](https://github.com/eamigo86/graphene-django-extras/issues)
- 💬 [Repository](https://github.com/eamigo86/graphene-django-extras)

## Acknowledgments

Special thanks to all contributors who have helped make `graphene-django-extras` better:

- The GraphQL and Graphene communities
- Django REST Framework team
- All issue reporters and pull request contributors
- Documentation contributors and reviewers

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*For the complete version history and detailed changes, see the [GitHub releases page](https://github.com/eamigo86/graphene-django-extras/releases).*