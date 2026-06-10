#!/usr/bin/env python3
import json
import sys
from graphql import build_schema, parse, GraphQLNonNull, GraphQLList, GraphQLEnumType, GraphQLInputObjectType, GraphQLScalarType

# Default values for scalar types
SCALAR_DEFAULTS = {
    'Int': 0,
    'Float': 0.0,
    'String': 'example',
    'Boolean': False,
    'ID': 'example-id'
}

def get_default_value(gql_type):
    """Recursively generate default values for a GraphQL type."""
    if isinstance(gql_type, GraphQLNonNull):
        return get_default_value(gql_type.of_type)
    if isinstance(gql_type, GraphQLList):
        return []
    if isinstance(gql_type, GraphQLEnumType):
        # Return the first enum value
        return list(gql_type.values.keys())[0] if gql_type.values else None
    if isinstance(gql_type, GraphQLScalarType):
        return SCALAR_DEFAULTS.get(gql_type.name, None)
    if isinstance(gql_type, GraphQLInputObjectType):
        obj = {}
        for name, field in gql_type.fields.items():
            obj[name] = get_default_value(field.type)
        return obj
    return None

def fix_variables(variables, var_defs, schema):
    """Fix variables according to schema types."""
    fixed_vars = {}
    for var_def in var_defs:
        var_name = var_def.variable.name.value
        type_node = var_def.type
        # Resolve GraphQL type from schema
        gql_type = type_from_ast(schema, type_node)
        # If variable exists and matches type, keep it; otherwise, replace with default
        fixed_vars[var_name] = get_default_value(gql_type)
    return fixed_vars

def type_from_ast(schema, type_node):
    """Resolve GraphQLType from AST node."""
    from graphql import GraphQLNonNull, GraphQLList
    if type_node.kind == 'non_null_type':
        return GraphQLNonNull(type_from_ast(schema, type_node.type))
    if type_node.kind == 'list_type':
        return GraphQLList(type_from_ast(schema, type_node.type))
    if type_node.kind == 'named_type':
        type_name = type_node.name.value
        return schema.get_type(type_name)
    return None

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 fixit.py collection.json schema.graphql")
        sys.exit(1)

    collection_file = sys.argv[1]
    schema_file = sys.argv[2]

    # Load Postman collection
    with open(collection_file) as f:
        collection = json.load(f)

    # Load GraphQL schema
    with open(schema_file) as f:
        schema_sdl = f.read()
    schema = build_schema(schema_sdl)

    # Iterate through collection items
    for item in collection.get("item", []):
        request = item.get("request", {})
        body = request.get("body", {})
        if body.get("mode") != "graphql":
            continue

        graphql_body = body.get("graphql", {})
        query = graphql_body.get("query", "")
        if not query:
            continue

        variables = graphql_body.get("variables", {})

        # Parse query to get variable definitions
        parsed = parse(query)
        for defn in parsed.definitions:
            if hasattr(defn, "variable_definitions"):
                fixed = fix_variables(variables, defn.variable_definitions, schema)
                graphql_body["variables"] = fixed

    # Save fixed collection
    output_file = "collection_fixed.json"
    with open(output_file, "w") as f:
        json.dump(collection, f, indent=2)

    print(f"Fixed collection saved to {output_file}")

if __name__ == "__main__":
    main()
