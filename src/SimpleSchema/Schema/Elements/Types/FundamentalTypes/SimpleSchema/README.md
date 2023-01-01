# Fundamental Types

This directory contains all of the fundamental types available when defining a SimpleSchema schema. As a proof-of-concept, these types are themselves defined via the SimpleSchema definition language.

Each type outlines the metadata that can be used to customize the type itself (for example, specifying a minimum value for an `Integer`). All types can be decorated with the metadata found in [Traits/Type.SimpleSchema](Traits/Type.SimpleSchema).

## Collection Types

A Collection Type is a type with a maximum cardinality that is greater than 1.

```
ZeroOrMoreStrings: String*                  # <-- Collection Type
OneOrMoreStrings: String*                   # <-- Collection Type

NotACollection: String                      # <-- Not a Collection Type
```

The metadata associated with Collection Types can be customized with the values found in [Traits/Collection.SimpleSchema](Traits/Collection.SimpleSchema).

## Optional Types

An Optional Type is a type with a minimum cardinality of 0 and a maximum cardinality of 1.

```
OptionalType1: String?                      # <-- Optional
OptionalType2: String [0, 1]                # <-- Optional

RequiredType: String                        # <-- Not Optional
```

The metadata associated with Optional Types can be customized with the values found in [Traits/Optional.SimpleSchema](Traits/Optional.SimpleSchema).

## Types

The metadata associated with Types can be customized with the values found in [Traits/Type.SimpleSchema](Triats/Type.SimpleSchema).
