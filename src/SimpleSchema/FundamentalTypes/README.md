# Fundamental Types

This directory contains all of the fundamental types available when defining a SimpleSchema schema. As a proof-of-concept, these types are themselves defined via the SimpleSchema definition language.

Each type outlines the metadata that can be used to customize the type itself (for example, specifying a minimum value for an `Integer`). All types can be decorated with the metadata found in [Traits/Type.SimpleSchema](Traits/Type.SimpleSchema).

## Collection Types

A Collection Type is a type with a maximum cardinality that is greater than 1.

```
ZeroOrMoreStrings: String { cardinality: * }            # <-- Collection Type
OneOrMoreStrings: String { cardinality: * }             # <-- Collection Type

NotACollection: String                                  # <-- Not a Collection Type
```

The metadata associated with Collection Types can be customized with the values found in [Traits/Collection.SimpleSchema](Traits/Collection.SimpleSchema).

## Compound Types

A Compound Type is a type that contains child attributes or type definitions. This is different from a data type, which is a single piece of data.

```
Person ->                                   # <-- Compound Type
    first_name: String                      # <-- Not a Compound Type
    last_name: String                       # <-- Not a Compound Type
    age: Integer { min: 0, max: 120 }       # <-- Not a Compound Type
```

The metadata associated with Compound Types can be customized with the values found in [Traits/Compound.SimpleSchema](Traits/Compound.SimpleSchema).

## Optional Types

An Optional Type is a type with a minimum cardinality of 0 and a maximum cardinality of 1.

```
OptionalType1: String { cardinality: ? }    # <-- Optional

OptionalType2: String {                     # <-- Optional
    cardinality:
        min: 0
        max: 1
}

RequiredType: String                        # <-- Not Optional
```

The metadata associated with Optional Types can be customized with the values found in [Traits/Optional.SimpleSchema](Traits/Optional.SimpleSchema).

## Reference Types

A Reference Type is a type that references a non-Fundamental type as a part of its definition.

```
CustomizedString: String { min_length: 10}  # <-- Not a Reference Type

ReferenceType: CustomizedString             # <-- Reference Type
```

The metadata associated with Reference Types can be customized with the values found in [Traits/ReferenceType.SimpleSchema](Traits/ReferenceType.SimpleSchema).
